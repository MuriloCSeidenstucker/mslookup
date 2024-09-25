import logging
from typing import Dict, List, Union

from src.products.medicine import Medicine
from src.products.product import Product
from src.search_in_open_data_anvisa import OpenDataAnvisa
from src.search_in_smerp import SearchInSmerp


class SearchProcessor:
    def __init__(self) -> None:
        self.logger = logging.getLogger(
            f'main_logger.{self.__class__.__name__}'
        )
        self.anvisa_search = OpenDataAnvisa()
        self.smerp_search = SearchInSmerp()

    # Consegue obter registros apenas de medicamentos.
    # Deverá ser estendido no momento da inclusão dos novos tipos de produtos
    def try_search_registrations(
        self, product: Product
    ) -> List[Dict[str, Union[str, int]]]:
        self.logger.info(
            f'Fetching registration data for item: {product.item_number}'
        )
        registrations = []

        if isinstance(product, Medicine):
            registrations = self.get_medicine_registrations(product)

        return registrations

    def get_medicine_registrations(
        self, medicine: Medicine
    ) -> List[Dict[str, Union[str, int]]]:
        description_temp = (
            medicine.extracted_substances
            if medicine.extracted_substances is not None
            else medicine.description
        )
        registrations = self.anvisa_search.get_register(
            description_temp, medicine.brand
        )
        if registrations:
            self.logger.info(
                f'Found {len(registrations)} candidates in ANVISA data\n'
            )
        else:
            self.logger.info(
                'No candidates found in ANVISA data, searching in SMERP'
            )
            registrations = self.smerp_search.get_data_from_smerp(
                description_temp, medicine.brand
            )
            if registrations:
                self.logger.info(
                    f'Found {len(registrations)} candidates in SMERP data\n'
                )
            else:
                self.logger.warning(
                    'No candidates found in both ANVISA and SMERP data\n'
                )

        return registrations
