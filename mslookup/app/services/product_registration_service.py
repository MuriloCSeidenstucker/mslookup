from typing import List

from mslookup.app.products.product import Product
from mslookup.app.registration_processors.registration_processor import RegistrationProcessor
from mslookup.app.logger_config import get_logger

class ProductRegistrationService:
    def __init__(self, checkpoint_manager):
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info('Instantiated.')
        
        self.registration_processor = RegistrationProcessor(checkpoint_manager)

    def get_product_registrations(self, processed_input: List[Product], progress_callback=None) -> List[Product]:
        self.logger.info('Starting service execution.')
        product_registrations = []
        product_registrations = (
            self.registration_processor.process_registrations(
                processed_input,
                progress_callback
            )
        )
        
        self.logger.info('Service execution completed.')
        return product_registrations
