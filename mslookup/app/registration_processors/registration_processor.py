from typing import List

from mslookup.app.products.product import Product
from mslookup.app.registration_processors.search_processor import SearchProcessor
from mslookup.app.logger_config import get_logger

class RegistrationProcessor:
    def __init__(self, checkpoint_manager):
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info('Instantiated.')
        
        self.search_processor = SearchProcessor()
        self.checkpoint_manager = checkpoint_manager
        self.checkpoint_interval = 10

    def process_registrations(self, processed_input: List[Product], progress_callback=None) -> List[Product]:
        self.logger.info('Starting execution.')
        product_registrations = []

        current_identifier = self.checkpoint_manager.generate_identifier(
            processed_input
        )
        checkpoint, saved_identifier = self.checkpoint_manager.load_checkpoint(
            stage='candidate_service'
        )
        if saved_identifier == current_identifier:
            product_registrations.extend(checkpoint['data'])
            start_index = len(product_registrations)
        else:
            start_index = 0

        total_products = len(processed_input)
        progress_step = 40 / total_products if total_products > 0 else 0
        for index, product in enumerate(processed_input[start_index:]):
            registers = self.search_processor.try_get_registrations(product)
            product.registers = registers

            product_registrations.append(product)
            
            if progress_callback:
                progress_callback(min(60, 20 + (index + 1) * progress_step))

            if len(product_registrations) % self.checkpoint_interval == 0:
                self.checkpoint_manager.save_checkpoint(
                    product_registrations,
                    'candidate_service',
                    current_identifier,
                )

        self.checkpoint_manager.save_checkpoint(
            product_registrations, 'candidate_service', current_identifier
        )
        
        if progress_callback:
            progress_callback(60)
            
        self.logger.info('Execution completed.')
        return product_registrations
