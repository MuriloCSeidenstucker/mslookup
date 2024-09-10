from src.products.medicine import Medicine

class InputManager:
    def get_raw_input(self):
        file_path = self.get_file_path()
        products_type = self.get_products_type()
        item_col = self.get_item_column_name()
        desc_col = self.get_description_column_name()
        brand_col = self.get_brand_column_name()
        
        entry = {
            'file_path': file_path,
            'products_type': products_type,
            'item_col': item_col,
            'desc_col': desc_col,
            'brand_col': brand_col
        }
        
        return entry
    
    def get_file_path(self):
        path = r"data_for_testing\test_quick_4.xlsm"
        return path
    
    def get_products_type(self):
        products_type = Medicine
        return products_type
    
    def get_item_column_name(self):
        name = 'ITEM'
        return name
    
    def get_description_column_name(self):
        name = 'DESCRIÇÃO'
        return name
    
    def get_brand_column_name(self):
        name = 'MARCA'
        return name