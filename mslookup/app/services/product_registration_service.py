import logging
from typing import List

from mslookup.app.logger_config import configure_logging
from mslookup.app.products.product import Product
from mslookup.app.registration_processors.registration_processor import \
    RegistrationProcessor


class ProductRegistrationService:
    def __init__(self, checkpoint_manager):
        configure_logging()
        self.name = self.__class__.__name__
        logging.info(f'{self.name}: Instantiated.')
        
        self.registration_processor = RegistrationProcessor(checkpoint_manager)

    def get_product_registrations(self, processed_input: List[Product], progress_callback=None) -> List[Product]:
        logging.info(f'{self.name}: Starting execution.')
        product_registrations = []
        product_registrations = (
            self.registration_processor.process_registrations(processed_input, progress_callback)
        )
        
        logging.info(f'{self.name}: Execution completed.')
        return product_registrations
