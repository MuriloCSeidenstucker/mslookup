import pandas as pd

from typing import Set, Tuple

from mslookup.app.utils import Utils
from mslookup.app.json_manager import JsonManager
from mslookup.app.df_manager import load_data
from mslookup.app.logger_config import get_logger

class DescriptionProcessor:
    def __init__(self) -> None:
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info('Instantiated.')
        
        self.json_manager = JsonManager(r'data\resources\stop_words.json')
        self.STOP_WORDS = self.json_manager.load_json()

        anvisa_spreadsheet_path = r'data\anvisa\TA_PRECO_MEDICAMENTO_GOV.xlsx'
        parquet_path = r'data\anvisa\TA_PRECO_MEDICAMENTO_GOV.parquet'
        skiprows = 52
        selected_columns = [
            'SUBSTÂNCIA',
            'CNPJ',
            'LABORATÓRIO',
            'EAN 1',
            'PRODUTO',
            'APRESENTAÇÃO',
        ]
        self.anvisa_df = load_data(anvisa_spreadsheet_path, parquet_path, skiprows, selected_columns)
        self.substances_set, self.shortest_substance = self.process_substances()

    def process_substances(self) -> Tuple[Set[str], int]:
        substances_set = set()
        shortest_length = float('inf')

        for row in self.anvisa_df['SUBSTÂNCIA']:
            if pd.notna(row):
                row_str = str(row)
                if ';' in row_str:
                    substances = row_str.split(';')
                    for substance in substances:
                        substance = substance.strip()
                        substances_set.add(substance)

                        if len(substance) < shortest_length:
                            shortest_length = len(substance)
                else:
                    substance = row_str.strip()
                    substances_set.add(substance)

                    if len(substance) < shortest_length:
                        shortest_length = len(substance)

        return sorted(substances_set, key=len, reverse=True), shortest_length

    def try_get_substances(self, description: str) -> str:
        extracted_substances = ''
        description_normalized = Utils.remove_accents_and_spaces(description)

        for substance in self.substances_set:

            if self.shortest_substance > len(description_normalized):
                break

            sub_normalized = Utils.remove_accents_and_spaces(substance)
            if len(sub_normalized) > len(description_normalized):
                continue

            if sub_normalized in description_normalized:
                extracted_substances += f'{substance};'
                description_normalized = description_normalized.replace(
                    sub_normalized, ''
                )

        if extracted_substances:
            return extracted_substances.rstrip(';')
        else:
            # As descrições dos medicamentos podem trazer substâncias fora da ordem esperada, por exemplo: Sódio Cloreto.
            for substance in self.substances_set:
                substance_words = [
                    Utils.remove_accents_and_spaces(word)
                    for word in substance.split()
                ]
                substance_words_clean = [
                    word
                    for word in substance_words
                    if len(word) >= self.shortest_substance
                ]
                substance_words_clean = [
                    word
                    for word in substance_words_clean
                    if word not in self.STOP_WORDS['stop_words']
                ]
                for sub in substance_words_clean:
                    if sub in description_normalized:
                        extracted_substances += f'{sub};'
                        description_normalized = (
                            description_normalized.replace(sub, '')
                        )

            if extracted_substances:
                return extracted_substances.rstrip(';')
            else:
                return None
