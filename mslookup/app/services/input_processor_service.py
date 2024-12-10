from typing import Dict, List

from mslookup.app.products.product import Product
from mslookup.app.input_processors.input_processor import InputProcessor
from mslookup.app.logger_config import get_logger

class InputProcessorService:
    def __init__(self, checkpoint_manager):
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info('Instantiated.')
        
        self.input_processor = InputProcessor(checkpoint_manager)

    def get_processed_input(self, raw_input: Dict[str, str], progress_callback=None) -> List[Product]:
        self.logger.info('Starting service execution.')
        processed_input = []
        processed_input = self.input_processor.process_input(raw_input, progress_callback)
        self.logger.info('Service execution completed.')
        return processed_input
