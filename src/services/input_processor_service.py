from typing import Any, Dict, List
from src.input_processors.input_processor import InputProcessor

class InputProcessorService:
    def __init__(self, checkpoint_manager):
        self.input_processor = InputProcessor(checkpoint_manager)
    
    def get_processed_input(self, raw_input: Dict[str, str]) -> List[Dict[str, Any]]:
        processed_input = []
        processed_input = self.input_processor.process_input(raw_input)
        return processed_input