from typing import List, Dict, Any

import pandas as pd

from scripts.input_processors.brand_processor import BrandProcessor
from scripts.input_processors.description_processor import DescriptionProcessor
from scripts.input_processors.concentration_processor import ConcentrationProcessor

class InputProcessor:
    def __init__(self, checkpoint_manager):
        self.brand_processor = BrandProcessor()
        self.description_processor = DescriptionProcessor()
        self.concentration_processor = ConcentrationProcessor()
        
        self.checkpoint_interval = 10
        self.checkpoint_manager = checkpoint_manager
        
    def read_raw_input(self, raw_input: Dict[str, str]) -> List[Dict[str, str]]:
        filtered_input = []
        file_path = raw_input['file_path']
        item_col = raw_input['item_col']
        desc_col = raw_input['desc_col']
        brand_col = raw_input['brand_col']
        
        df = pd.read_excel(file_path)
        for index, row in df.iterrows():
            if pd.notna(row[brand_col]):
                filtered_input.append({
                    'item': row[item_col],
                    'description': row[desc_col],
                    'brand': row[brand_col]
                })
        
        return filtered_input

    def process_input(self, raw_input: Dict[str, str]) -> List[Dict[str, Any]]:
        filtered_input = self.read_raw_input(raw_input)
        
        data = []
        
        current_identifier = self.checkpoint_manager.generate_identifier(filtered_input)
        checkpoint, saved_identifier = self.checkpoint_manager.load_checkpoint(stage='data_processor')
        if saved_identifier == current_identifier:
            data.extend(checkpoint['data'])
            start_index = len(data)
        else:
            start_index = 0
            
        for index, row in enumerate(filtered_input[start_index:]):
            brand = self.brand_processor.get_brand(row['brand'])
            filtered_description = self.description_processor.get_filtered_description(row['description'])
            concentration = self.concentration_processor.get_concentration(row['description'])
            data.append({
                'item': row['item'],
                'origin_description': row['description'],
                'description': filtered_description,
                'brand': brand,
                'concentration': concentration
            })
                        
            if len(data) % self.checkpoint_interval == 0:
                self.checkpoint_manager.save_checkpoint(data, 'data_processor', current_identifier)
                
        self.checkpoint_manager.save_checkpoint(data, 'data_processor', current_identifier)
            
        return data