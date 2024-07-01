from data_processor import DataProcessor

class DataProcessorService:
    def __init__(self, file_path, item_col, desc_col, brand_col):
        self.data_processor = DataProcessor(file_path)
        self.data = self.data_processor.get_data(item_col, desc_col, brand_col)
    
    def get_data(self):
        return self.data