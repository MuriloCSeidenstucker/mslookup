from typing import Any, Dict, Union

from scripts.utils import Utils
from scripts.json_manager import load_json

class BrandProcessor:
    def __init__(self) -> None:
        self.labs_path = 'laboratories.json'
        self.labs_json = load_json(self.labs_path)
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