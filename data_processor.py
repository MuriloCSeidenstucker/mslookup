import os
import json
import pandas as pd

from utils import Utils

class DataProcessor:
    def __init__(self, file_path):
        self.df = pd.read_excel(file_path)
        
        with open('laboratories.json', 'r', encoding='utf-8') as file:
            self.labs_json = json.load(file)
        self.abbreviation_map = self.create_abbreviation_map()
        
        reference_path = os.path.join(os.path.dirname(__file__), 'TA_PRECO_MEDICAMENTO_GOV.xlsx')
        self.reference_df = pd.read_excel(reference_path, skiprows=52)
        self.substances_set, self.shortest_substance = self.process_substances()
        print(f'{len(self.substances_set)}, menor: {self.shortest_substance}')
            
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
    
    def process_substances(self):
        substances_set = set()
        shortest_length = float('inf')
        
        for row in self.reference_df['SUBSTÂNCIA']:
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

        return substances_set, shortest_length

    
    def get_brand(self, brand):
        brand_normalized = Utils.remove_accents_and_spaces(brand)

        if brand_normalized in self.abbreviation_map:
            return self.abbreviation_map[brand_normalized]

        print(f"A marca: {brand} não foi encontrada no banco de dados")
        return brand
    
    def get_filtered_description(self, description):
        
        filtered_desc = ''
        description_normalized = Utils.remove_accents_and_spaces(description)
        
        for substance in self.substances_set:
            
            if self.shortest_substance > len(description_normalized):
                break
            
            sub_normalized = Utils.remove_accents_and_spaces(substance)
            if len(sub_normalized) > len(description_normalized):
                continue
            
            if sub_normalized in description_normalized:
                filtered_desc += f'{substance};'
                
        if filtered_desc:
            if filtered_desc.endswith(';'):
                filtered_desc = filtered_desc[:-1]
            return filtered_desc
        else:
            return description

    def get_data(self, item_col, desc_col, brand_col):
        data = []
        for index, row in self.df.iterrows():
            if pd.notna(row[brand_col]):
                brand = self.get_brand(row[brand_col])
                description = self.get_filtered_description(row[desc_col])
                data.append({'item': row[item_col], 'description': description, "brand": brand})
        return data
                        
                    