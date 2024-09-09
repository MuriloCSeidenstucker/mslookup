import re

from scripts.json_manager import load_json

class ConcentrationProcessor:
    def __init__(self) -> None:
        self.patterns_path = r'resources\patterns.json'
        self.patterns = load_json(self.patterns_path)
    
    def get_concentration(self, description: str) -> str:
        lower_description = description.lower()
        for pattern in self.patterns["patterns"]:
            match = re.search(pattern, lower_description)
            if match:
                return match.group()
        return "Concentração não encontrada"