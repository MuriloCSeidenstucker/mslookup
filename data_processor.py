import re
import time
from unidecode import unidecode
import os
import json
import pandas as pd

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
                f_abbreviation = self.remove_accents_and_spaces(abbreviation)
                lab_info = {
                    "Name": lab['full_name'],
                    "CNPJ": lab['cnpj']
                }
                linked = lab.get('linked')
                if linked is not None:
                    lab_info['Linked'] = linked
                abbreviation_map[f_abbreviation] = lab_info
        
        return abbreviation_map

    def get_data(self, item_col, desc_col, brand_col):
        data = []
        for index, row in self.df.iterrows():
            if pd.notna(row[brand_col]):
                brand= self.get_brand(row[brand_col])
                description = self.get_filtered_description(row[desc_col], brand)
                data.append({'item': row[item_col], 'description': description, "brand": brand})
        return data
    
    def remove_accents_and_spaces(self, input_str):
        return unidecode(input_str.replace(" ", "").lower()) if isinstance(input_str, str) else input_str
    
    def get_filtered_description(self, description, brand):
        description_normalized = self.remove_accents_and_spaces(description)

        for _, ref_row in self.reference_df.iterrows():
            ref_subs_normalized = self.remove_accents_and_spaces(str(ref_row['SUBSTÂNCIA']))
            ref_prod_normalized = self.remove_accents_and_spaces(str(ref_row['PRODUTO']))
            # ref_apres_normalized = self.remove_accents_and_spaces(str(ref_row['APRESENTAÇÃO']))
            pattern = r'\D'
            ref_cnpj = re.sub(pattern, '', str(ref_row['CNPJ']))

            if (ref_subs_normalized in description_normalized or
                ref_prod_normalized in description_normalized):
                if not isinstance(brand, str):
                    if ref_cnpj == brand['CNPJ']:
                        corresp_subst = ''
                        corresp_prod = ''
                        # corresp_apres = ''

                        # if ref_apres_normalized in description_normalized:
                        #     corresp_apres = ref_row['APRESENTAÇÃO']
                            
                        corresp_subst = ref_row['SUBSTÂNCIA']
                        corresp_prod = ref_row['PRODUTO']

                        filtered_description = f"{corresp_subst} {corresp_prod}"
                        return filtered_description

        return description
    
    def get_brand(self, brand):
        f_brand = self.remove_accents_and_spaces(brand)

        if f_brand in self.abbreviation_map:
            return self.abbreviation_map[f_brand]

        print(f"A marca: {brand} não foi encontrada no banco de dados")
        return brand
                        
                    