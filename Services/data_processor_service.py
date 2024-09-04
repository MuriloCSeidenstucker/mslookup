from typing import Dict
from data_processor import DataProcessor

class DataProcessorService:
    def __init__(self, entry: Dict, checkpoint_manager):
        self.data_processor = DataProcessor(entry['file_path'], checkpoint_manager)
        self.data = self.data_processor.get_data(entry['item_col'], entry['desc_col'], entry['brand_col'])
    
    def get_data(self):
        return self.data