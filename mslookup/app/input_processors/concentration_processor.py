import re

from mslookup.app.json_manager import JsonManager
from mslookup.app.logger_config import get_logger

class ConcentrationProcessor:
    def __init__(self) -> None:
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info('Instantiated.')
        
        self.json_manager = JsonManager(r'data\resources\patterns.json')
        self.patterns = self.json_manager.load_json()

    def get_concentration(self, description: str) -> str:
        value = 'Concentração não encontrada'
        lower_description = description.lower()
        for pattern in self.patterns['patterns']:
            match = re.search(pattern, lower_description)
            if match:
                value = match.group()
                break
            
        return value
