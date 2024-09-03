class Input:
    def start(self):
        print('[input] Starting...')
        file_path = self.get_file_path()
        item_col = self.get_item_column_name()
        desc_col = self.get_description_column_name()
        brand_col = self.get_brand_column_name()
        
        entry = {
            'file_path': file_path,
            'item_col': item_col,
            'desc_col': desc_col,
            'brand_col': brand_col
        }
        
        print('[input] Starting done!')
        return entry
    
    def get_file_path(self):
        path = r"data_for_testing\Controle_Operacao_PE_042024_Frutal.xlsm"
        return path
    
    def get_item_column_name(self):
        name = 'ITEM'
        return name
    
    def get_description_column_name(self):
        name = 'DESCRIÇÃO'
        return name
    
    def get_brand_column_name(self):
        name = 'MARCA'
        return name