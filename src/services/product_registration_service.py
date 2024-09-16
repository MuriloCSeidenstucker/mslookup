from typing import List

from src.products.product import Product
from src.registration_processors.registration_processor import RegistrationProcessor

class ProductRegistrationService:
    def __init__(self, checkpoint_manager):
        self.registration_processor = RegistrationProcessor(checkpoint_manager)
    
    def get_product_registrations(self, processed_input: List[Product]) -> List[Product]:
        product_registrations = []
        product_registrations = self.registration_processor.process_registrations(processed_input)
        return product_registrations