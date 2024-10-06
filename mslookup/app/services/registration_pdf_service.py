import logging
from datetime import datetime
from typing import Any, Dict, List

from mslookup.app.access_anvisa_domain import AnvisaDomain
from mslookup.app.json_manager import JsonManager
from mslookup.app.pdf_manager import PDFManager
from mslookup.app.products.medicine import Medicine
from mslookup.app.products.product import Product


class RegistrationPDFService:
    def __init__(self, pdf_manager: PDFManager, anvisa_domain: AnvisaDomain):
        self.logger = logging.getLogger(
            f'main_logger.{self.__class__.__name__}'
        )
        self.pdf_manager = pdf_manager
        self.anvisa_domain = anvisa_domain
        self.json_manager = JsonManager(r'data\resources\pdf_db.json')

    def generate_registration_pdfs(
        self, product_registrations: List[Product]
    ) -> List[Dict[str, Any]]:
        final_result = []
        reg_data = {}
        data_updated = False

        for product_index, product in enumerate(product_registrations):
            final_result.append(
                {
                    'Item': product.item_number,
                    'Descrição': product.description,
                    'Concentração_Encontrada': product.concentration,
                    'Marca': product.brand
                    if isinstance(product.brand, str)
                    else product.brand['Name'],
                    'Registro': '',
                    'PDF': '',
                }
            )

            data_modified = False

            if not product.registers:
                final_result[product_index]['Registro'] = 'Não encontrado'
                final_result[product_index]['PDF'] = 'Pendente'
                continue

            if isinstance(product, Medicine):
                for reg_index, reg in enumerate(product.registers):
                    has_pdf_in_db = self.pdf_manager.get_pdf_in_db(
                        reg['register'], product.concentration, data_updated
                    )

                    registration_obtained = False
                    if not has_pdf_in_db:
                        registration_obtained = (
                            self.anvisa_domain.get_register_as_pdf(
                                reg['register'],
                                product.concentration,
                                reg['expiration_date'],
                                reg_data,
                            )
                        )
                        if registration_obtained:
                            data_modified = True
                            self.pdf_manager.copy_and_rename_file(
                                reg['register'], reg['expiration_date']
                            )

                    has_pdf = False
                    if has_pdf_in_db or registration_obtained:
                        has_pdf = self.pdf_manager.rename_downloaded_pdf(
                            f'Item {product.item_number}'
                        )

                    if has_pdf:
                        final_result[product_index]['Registro'] = (
                            reg['register']
                            if reg['register'] != -1
                            else 'Não encontrado'
                        )
                        final_result[product_index]['PDF'] = (
                            'OK' if has_pdf else 'Pendente'
                        )
                        break

                    if reg_index == len(product.registers) - 1:
                        final_result[product_index]['Registro'] = (
                            f'Último registro encontrado: {reg['register']}'
                            if reg['register'] != -1 else 'Não encontrado'
                        )
                        final_result[product_index]['PDF'] = (
                            'OK' if has_pdf else 'Pendente'
                        )

            if data_modified:
                self.generate_json_file(
                    reg_data, r'data\resources\pdf_db.json'
                )
                data_updated = True
            else:
                data_updated = False

        return final_result

    def generate_json_file(
        self, data: Dict[str, Dict[str, List[str]]], filename: str
    ) -> None:
        try:
            existing_data = self.json_manager.load_json()

            for key, value in data.items():
                if key not in existing_data:
                    existing_data[key] = value
                else:
                    updated_presentations = set(
                        existing_data[key]['presentations']
                    ).union(set(value['presentations']))
                    existing_data[key]['presentations'] = list(
                        updated_presentations
                    )

                    existing_exp_date_str = existing_data[key][
                        'expiration_date'
                    ]
                    new_exp_date_str = value['expiration_date']

                    if (
                        isinstance(existing_exp_date_str, str)
                        and existing_exp_date_str != 'nan'
                        and existing_exp_date_str != 'DATA INVÁLIDA'
                    ):
                        existing_expiration_date = datetime.strptime(
                            existing_exp_date_str, '%d/%m/%Y'
                        )
                    else:
                        existing_expiration_date = datetime.min

                    if (
                        isinstance(new_exp_date_str, str)
                        and new_exp_date_str != 'nan'
                    ):
                        new_expiration_date = datetime.strptime(
                            new_exp_date_str, '%d/%m/%Y'
                        )
                    else:
                        new_expiration_date = datetime.min

                    if new_expiration_date > existing_expiration_date:
                        existing_data[key]['expiration_date'] = value[
                            'expiration_date'
                        ]

            self.json_manager.write_json(existing_data)
            self.logger.info(f'JSON file successfully generated: "{filename}"')
        except (IOError, TypeError) as e:
            self.logger.error(
                f"Failed to generate JSON file '{filename}': {e}"
            )
            raise
