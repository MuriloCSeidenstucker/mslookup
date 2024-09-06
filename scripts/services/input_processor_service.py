import pandas as pd

from typing import Any, Dict, List

from scripts.input_processor.data_processor import DataProcessor

class InputProcessorService:
    def __init__(self, checkpoint_manager):
        self.data_processor = DataProcessor(checkpoint_manager)
    
    def get_processed_input(self, raw_input: Dict[str, str]) -> List[Dict[str, Any]]:
        processed_input = []
        
        filtered_input = self.read_raw_input(raw_input)
        processed_input = self.data_processor.process_input(filtered_input)
        
        return processed_input
    
    def read_raw_input(self, raw_input: Dict[str, str]):
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