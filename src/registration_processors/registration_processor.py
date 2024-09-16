import logging

from typing import List

from src.products.product import Product
from src.registration_processors.search_processor import SearchProcessor

class RegistrationProcessor:
    def __init__(self, checkpoint_manager):
        self.logger = logging.getLogger(f'main_logger.{self.__class__.__name__}')
        self.search_processor = SearchProcessor()
        
        self.checkpoint_manager = checkpoint_manager
        self.checkpoint_interval = 10
    
    def process_registrations(self, processed_input: List[Product]) -> List[Product]:
        product_registrations = []
        
        current_identifier = self.checkpoint_manager.generate_identifier(processed_input)
        checkpoint, saved_identifier = self.checkpoint_manager.load_checkpoint(stage='candidate_service')
        if saved_identifier == current_identifier:
            product_registrations.extend(checkpoint['data'])
            start_index = len(product_registrations)
        else:
            start_index = 0
        
        for index, product in enumerate(processed_input[start_index:]):
            registers = self.search_processor.try_search_registrations(product)
            product.registers = registers
            
            product_registrations.append(product)
                                    
            if len(product_registrations) % self.checkpoint_interval == 0:
                self.checkpoint_manager.save_checkpoint(product_registrations, 'candidate_service', current_identifier)
            
        self.checkpoint_manager.save_checkpoint(product_registrations, 'candidate_service', current_identifier)
        
        self.logger.info('Candidate data generation complete\n\n')
        return product_registrations