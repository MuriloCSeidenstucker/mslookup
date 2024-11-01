import logging
from typing import Any, Dict, List

from mslookup.app.input_processors.input_processor import InputProcessor
from mslookup.app.logger_config import configure_logging


class InputProcessorService:
    def __init__(self, checkpoint_manager):
        configure_logging()
        self.name = self.__class__.__name__
        logging.info(f'{self.name}: Instantiated.')
        self.input_processor = InputProcessor(checkpoint_manager)

    def get_processed_input(self, raw_input: Dict[str, str]) -> List[Dict[str, Any]]:
        logging.info(f'{self.name}: Starting execution.')
        processed_input = []
        processed_input = self.input_processor.process_input(raw_input)
        logging.info(f'{self.name}: Execution completed.')
        return processed_input
