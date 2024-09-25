from typing import Any, Dict, Union

from src.utils import Utils
from src.json_manager import JsonManager

class BrandProcessor:
    def __init__(self) -> None:
        self.json_manager = JsonManager(r'data\resources\laboratories.json')
        self.labs_json = self.json_manager.load_json()
        self.abbreviation_map = self.create_abbreviation_map()
        
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
    
    def get_brand(self, brand: str) -> Union[Dict[str, str], str]:
        brand_normalized = Utils.remove_accents_and_spaces(brand)

        if brand_normalized in self.abbreviation_map:
            return self.abbreviation_map[brand_normalized]

        return brand