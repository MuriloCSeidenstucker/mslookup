class Input:
    def start(self):
        print('[input] Starting...')
        file_path = r"data_for_testing\Controle_Operacao_PE_090092024_Araxa.xlsm"
        item_col = 'ITEM'
        desc_col = 'DESCRIÇÃO'
        brand_col = 'MARCA'
        
        entry = {
            'file_path': file_path,
            'item_col': item_col,
            'desc_col': desc_col,
            'brand_col': brand_col
        }
        
        print('[input] Starting done!')
        return entry