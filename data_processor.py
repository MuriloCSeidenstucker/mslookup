import os
import re
import pandas as pd

from utils import Utils
from df_manager import load_data
from json_manager import load_json
from checkpoint_manager import CheckpointManager
from typing import List, Dict, Tuple, Union, Any

class DataProcessor:
    def __init__(self, file_path: str):
        self.df = pd.read_excel(file_path)
        self.checkpoint_interval = 2
        self.checkpoint_manager = CheckpointManager()
        
        self.patterns_path = 'patterns.json'
        self.patterns = load_json(self.patterns_path)
        
        self.prepositions_path = 'prepositions.json'
        self.PREPOSITIONS = load_json(self.prepositions_path)
        
        self.labs_path = 'laboratories.json'
        self.labs_json = load_json(self.labs_path)
        self.abbreviation_map = self.create_abbreviation_map()
        
        reference_path = os.path.join(os.path.dirname(__file__), 'TA_PRECO_MEDICAMENTO_GOV.xlsx')
        parquet_path = 'TA_PRECO_MEDICAMENTO_GOV.parquet'
        skiprows = 52
        selected_columns = ['SUBSTÂNCIA', 'CNPJ', 'LABORATÓRIO', 'EAN 1', 'PRODUTO', 'APRESENTAÇÃO']
        self.reference_df = load_data(reference_path, parquet_path, skiprows, selected_columns)
        self.substances_set, self.shortest_substance = self.process_substances()
        
    def get_concentration(self, description: str, patterns: List[str]) -> str:
        lower_description = description.lower()
        for pattern in patterns["patterns"]:
            match = re.search(pattern, lower_description)
            if match:
                return match.group()
        return "Concentração não encontrada"
            
    def create_abbreviation_map(self) -> Dict[str, Dict[str, Any]]:
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
    
    def process_substances(self) -> Tuple[List[str], int]:
        substances_set = set()
        shortest_length = float('inf')
        
        for row in self.reference_df['SUBSTÂNCIA']:
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
    
    def get_brand(self, brand: str) -> Union[Dict[str, str], str]:
        brand_normalized = Utils.remove_accents_and_spaces(brand)

        if brand_normalized in self.abbreviation_map:
            return self.abbreviation_map[brand_normalized]

        print(f"A marca: {brand} não foi encontrada no banco de dados")
        return brand
    
    def get_filtered_description(self, description: str) -> str:
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
                description_normalized = description_normalized.replace(sub_normalized, '')
                
        if filtered_desc:
            if filtered_desc.endswith(';'):
                filtered_desc = filtered_desc[:-1]
            return filtered_desc
        else:
            # As descrições dos medicamentos podem trazer substâncias fora da ordem esperada, por exemplo: Sódio Cloreto.
            for substance in self.substances_set:
                substance_words = [Utils.remove_accents_and_spaces(word) for word in substance.split()]
                substance_words_clean = [word for word in substance_words if len(word) >= self.shortest_substance]
                substance_words_clean = [word for word in substance_words_clean if word not in self.PREPOSITIONS['prepositions']]
                for sub in substance_words_clean:
                    if sub in description_normalized:
                        filtered_desc += f'{sub};'
                        description_normalized = description_normalized.replace(sub, '')
                        
            if filtered_desc:
                if filtered_desc.endswith(';'):
                    filtered_desc = filtered_desc[:-1]
                return filtered_desc
            else:
                return description

    def get_data(self, item_col: str, desc_col: str, brand_col: str) -> List[Dict[str, Any]]:
        data = []
        report_data = []
        
        current_identifier = self.checkpoint_manager.generate_identifier(self.df)
        checkpoint, saved_identifier = self.checkpoint_manager.load_checkpoint(stage='data_processor')
        if saved_identifier == current_identifier:
            data.extend(checkpoint['data'])
            start_index = len(data)
        else:
            start_index = 0
            
        for index, row in self.df.iloc[start_index:].iterrows():
            if pd.notna(row[brand_col]):
                brand = self.get_brand(row[brand_col])
                filtered_description = self.get_filtered_description(row[desc_col])
                concentration = self.get_concentration(row[desc_col], self.patterns)
                data.append({'item': row[item_col],
                             'origin_description': row[desc_col],
                             'description': filtered_description,
                             'brand': brand,
                             'concentration': concentration})
                
                report_data.append({'Item': row[item_col],
                        'Descrição Original': row[desc_col],
                        'Descrição Final': filtered_description,
                        'Concentração': concentration,
                        'Laboratório Original': row[brand_col],
                        'Laboratório Final': brand if isinstance(brand, str) else brand['Name'],
                        'Registro': '',
                        'PDF': '',
                        })
                        
            if len(data) % self.checkpoint_interval == 0:
                self.checkpoint_manager.save_checkpoint(data, stage='data_processor')
                
        report_df = pd.DataFrame(report_data)
        report_df.to_excel('relatorio_proc_dados.xlsx', index=False)
        
        self.checkpoint_manager.save_checkpoint(data, stage='data_processor')
            
        return data