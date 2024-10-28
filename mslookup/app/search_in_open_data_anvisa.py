from datetime import datetime
import logging
from typing import Any, Dict, List, Union

from mslookup.app.df_manager import load_data
from mslookup.app.logger_config import configure_logging
from mslookup.app.utils import Utils


class OpenDataAnvisa:
    def __init__(self):
        configure_logging()
        self.name = self.__class__.__name__
        
        file_path = r'data\anvisa\DADOS_ABERTOS_MEDICAMENTOS.xlsx'
        parquet_path = r'data\anvisa\DADOS_ABERTOS_MEDICAMENTOS.parquet'
        self.df = load_data(file_path, parquet_path)
        self.df = self.df[self.df['SITUACAO_REGISTRO'] == 'VÁLIDO'].copy()
        self.laboratory_registers = self.create_data_map()

    def create_data_map(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        laboratories = {}

        for index, row in self.df.iterrows():
            lab_cnpj, laboratory = str(
                row['EMPRESA_DETENTORA_REGISTRO']
            ).split(' ', 1)
            laboratory = laboratory.strip('- ')
            register = str(row['NUMERO_REGISTRO_PRODUTO'])
            product_name = str(row['NOME_PRODUTO'])
            expiration_date = str(row['DATA_VENCIMENTO_REGISTRO'])
            substances = (
                [
                    substance.strip()
                    for substance in str(row['PRINCIPIO_ATIVO']).split('+')
                ]
                if row['PRINCIPIO_ATIVO'] is not None
                else []
            )

            if laboratory not in laboratories:
                laboratories[laboratory] = {}

            if register not in laboratories[laboratory]:
                laboratories[laboratory][register] = {
                    'product_name': product_name,
                    'expiration_date': expiration_date,
                    'cnpj': lab_cnpj,
                    'substances': substances,
                }
            else:
                logging.info(
                    f'Registro {register} já existe no laboratório {laboratory}'
                )

        return laboratories

    def validate_arguments(
        self, description: str, laboratory: Union[str, Dict]
    ) -> None:
        if not isinstance(description, str) or not description.strip():
            raise ValueError('description deve ser uma string não vazia.')

        if not isinstance(laboratory, (str, dict)):
            raise ValueError(
                'laboratory deve ser uma string ou um dicionário.'
            )

        if isinstance(laboratory, dict):
            if (
                'Name' not in laboratory
                or not isinstance(laboratory['Name'], str)
                or not laboratory['Name'].strip()
            ):
                raise ValueError(
                    'O dicionário laboratory deve conter a chave "Name" com um valor string não vazio.'
                )
            if 'Linked' in laboratory and not isinstance(
                laboratory['Linked'], list
            ):
                raise ValueError(
                    'A chave "Linked" em laboratory, se presente, deve ser uma lista.'
                )

    def get_laboratory_candidates(self, laboratory: Union[str, Dict]) -> List[str]:
        if isinstance(laboratory, str):
            return [laboratory]

        if isinstance(laboratory, dict):
            candidates = [laboratory.get('Name', '')]
            linked = laboratory.get('Linked', [])
            if isinstance(linked, list):
                candidates.extend(linked)
            return [candidate for candidate in candidates if candidate]

        raise ValueError('laboratory deve ser uma string ou um dicionário.')

    def get_register(
        self, description: str, laboratory: Union[str, Dict]
    ) -> List[Dict[str, Union[str, int]]]:
        
        self.validate_arguments(description, laboratory)
        description_normalized = Utils.remove_accents_and_spaces(description)
        laboratory_candidates = self.get_laboratory_candidates(laboratory)

        reg_candidates_set = set()

        for laboratory_candidate in laboratory_candidates:
            # FIX: laboratory_candidate pode não ser uma chave.
            if laboratory_candidate in self.laboratory_registers:
                for register in self.laboratory_registers[
                    laboratory_candidate
                ]:
                    register_data = self.laboratory_registers[
                        laboratory_candidate
                    ][register]
                    selected_subs = description_normalized.split(';')
                    matches_count = len(selected_subs)
                    if len(register_data['substances']) != len(selected_subs):
                        continue
                    for substance in register_data['substances']:
                        sub_normalized = Utils.remove_accents_and_spaces(
                            substance
                        )
                        if sub_normalized in selected_subs:
                            matches_count -= 1
                            if matches_count == 0:
                                date_formatted = -1
                                if register_data['expiration_date'] != 'nan':
                                    date = datetime.strptime(
                                        register_data['expiration_date'],
                                        '%Y-%m-%d %H:%M:%S',
                                    )
                                    if isinstance(date, str) or isinstance(
                                        date, datetime
                                    ):
                                        date_formatted = date.strftime(
                                            '%d/%m/%Y'
                                        )
                                reg_candidates_set.add(
                                    (register, -1, date_formatted)
                                )

        # As descrições dos medicamentos podem trazer substâncias fora da ordem esperada, por exemplo: Sódio Cloreto.
        if not reg_candidates_set:
            words = description_normalized.split(';')
            for laboratory_candidate in laboratory_candidates:
                if laboratory_candidate in self.laboratory_registers:
                    for register in self.laboratory_registers[
                        laboratory_candidate
                    ]:
                        register_data = self.laboratory_registers[
                            laboratory_candidate
                        ][register]
                        for substance in register_data['substances']:
                            sub_normalized = Utils.remove_accents_and_spaces(
                                substance
                            )
                            if all(word in sub_normalized for word in words):
                                date_formatted = -1
                                if register_data['expiration_date'] != 'nan':
                                    date = datetime.strptime(
                                        register_data['expiration_date'],
                                        '%Y-%m-%d %H:%M:%S',
                                    )
                                    if isinstance(date, str) or isinstance(
                                        date, datetime
                                    ):
                                        date_formatted = date.strftime(
                                            '%d/%m/%Y'
                                        )
                                reg_candidates_set.add(
                                    (register, -1, date_formatted)
                                )

        reg_candidates = [
            {
                'register': reg[0],
                'process_number': reg[1],
                'expiration_date': reg[2],
            }
            for reg in reg_candidates_set
        ]

        return reg_candidates
