from typing import Dict

class InputManager:
    def get_raw_input(self) -> Dict[str, str]:
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
            'brand_col': brand_col,
        }
        
        return entry

    def get_file_path(self) -> str:
        # Apenas para testes:
        quick = r'data\testing\test_quick_4.xlsm'
        intermediate = r'data\testing\test_intermediate_14.xlsm'
        full = r'data\testing\test_full_126.xlsm'
        path = quick
        return path

    def get_products_type(self) -> str:
        products_type = 'medicine'
        return products_type

    def get_item_column_name(self) -> str:
        name = 'ITEM'
        return name

    def get_description_column_name(self) -> str:
        name = 'DESCRIÇÃO'
        return name

    def get_brand_column_name(self) -> str:
        name = 'MARCA'
        return name
