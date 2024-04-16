import re
import time
import os
import json
import pandas as pd

from unidecode import unidecode
from utils import Utils

class DataProcessor:
    def __init__(self, file_path):
        self.df = pd.read_excel(file_path)
        reference_path = os.path.join(os.path.dirname(__file__), 'TA_PRECO_MEDICAMENTO_GOV.xlsx')
        self.reference_df = pd.read_excel(reference_path, skiprows=52)
        with open('laboratories.json', 'r', encoding='utf-8') as file:
            self.labs_json = json.load(file)
        self.abbreviation_map = self.create_abbreviation_map()
            
    def create_abbreviation_map(self):
        laboratories = self.labs_json['laboratories']
        abbreviation_map = {}

        for lab in laboratories:
            for abbreviation in lab['abbreviations']:
                abbreviation_normalized = Utils.remove_accents_and_spaces(abbreviation)
                lab_info = {
                    "Name": lab['full_name'],
                    "CNPJ": lab['cnpj']
                }
                linked = lab.get('linked')
                if linked is not None:
                    lab_info['Linked'] = linked
                abbreviation_map[abbreviation_normalized] = lab_info
        
        return abbreviation_map
    
    def get_brand(self, brand):
        brand_normalized = Utils.remove_accents_and_spaces(brand)

        if brand_normalized in self.abbreviation_map:
            return self.abbreviation_map[brand_normalized]

        print(f"A marca: {brand} não foi encontrada no banco de dados")
        return brand
    
    def get_filtered_description(self, description, brand):
        description_normalized = Utils.remove_accents_and_spaces(description)

        for _, ref_row in self.reference_df.iterrows():
            ref_subs_normalized = Utils.remove_accents_and_spaces(str(ref_row['SUBSTÂNCIA']))
            ref_prod_normalized = Utils.remove_accents_and_spaces(str(ref_row['PRODUTO']))

            if (ref_subs_normalized in description_normalized or
                ref_prod_normalized in description_normalized):
                
                ref_lab_normalized = Utils.remove_accents_and_spaces(str(ref_row['LABORATÓRIO']))
                pattern = r'\D'
                ref_cnpj = re.sub(pattern, '', str(ref_row['CNPJ']))
                
                if not isinstance(brand, str):
                    if ref_cnpj == brand['CNPJ']:
                        return f'{str(ref_row['SUBSTÂNCIA'])} {str(ref_row['PRODUTO'])}'
                else:
                    brand_normalized = Utils.remove_accents_and_spaces(brand)
                    if brand_normalized in ref_lab_normalized:
                        return f'{str(ref_row['SUBSTÂNCIA'])} {str(ref_row['PRODUTO'])}'
            
        return description

    def get_data(self, item_col, desc_col, brand_col):
        data = []
        for index, row in self.df.iterrows():
            if pd.notna(row[brand_col]):
                brand= self.get_brand(row[brand_col])
                description = self.get_filtered_description(row[desc_col], brand)
                data.append({'item': row[item_col], 'description': description, "brand": brand})
        return data
                        
                    