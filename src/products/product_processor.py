from typing import Dict, Union

from src.products.product import Product
from src.products.medicine import Medicine
from src.input_processors.brand_processor import BrandProcessor
from src.input_processors.description_processor import DescriptionProcessor
from src.input_processors.concentration_processor import ConcentrationProcessor

class ProductProcessor:
    def __init__(self) -> None:
        self.brand_processor = BrandProcessor()
        self.description_processor = DescriptionProcessor()
        self.concentration_processor = ConcentrationProcessor()
    
    def get_processed_product(self, product_type: str, item_number: str, description: str, brand: str) -> Product:
        processed_product = None
        
        if product_type == 'medicine':
            processed_product = self.process_medicine(item_number, description, brand)
        else:
            raise ValueError(f'Unknow product type: {product_type}')
        
        return processed_product
        
    def process_medicine(self, item_number: str, description: str, brand: str) -> Medicine:
        processed_brand = self.brand_processor.get_brand(brand)
        concentration = self.concentration_processor.get_concentration(description)
        extracted_substances = self.description_processor.try_get_substances(description)
        
        processed_medicine = Medicine(
            item_number = item_number,
            description = description,
            brand = processed_brand,
            concentration = concentration,
            extracted_substances = extracted_substances
        )
        
        return processed_medicine