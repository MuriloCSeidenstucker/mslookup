import re

from src.json_manager import JsonManager

class ConcentrationProcessor:
    def __init__(self) -> None:
        self.json_manager = JsonManager(r'resources\patterns.json')
        self.patterns = self.json_manager.load_json()
    
    def get_concentration(self, description: str) -> str:
        lower_description = description.lower()
        for pattern in self.patterns["patterns"]:
            match = re.search(pattern, lower_description)
            if match:
                return match.group()
        return "Concentração não encontrada"