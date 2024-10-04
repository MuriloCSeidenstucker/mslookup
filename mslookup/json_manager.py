import json
import logging
from typing import Any, Dict


class JsonManager:
    def __init__(self, file_path: str):
        self.logger = logging.getLogger(
            f'main_logger.{self.__class__.__name__}'
        )
        self.file_path = file_path

    def load_json(self) -> Dict[str, Any]:
        try:
            with open(self.file_path, 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)
            return data
        except FileNotFoundError:
            self.logger.error(f'{self.file_path} not found.')
            return {}
        except json.JSONDecodeError as e:
            self.logger.error(f'Error decoding JSON file: {e}')
            return {}

    def write_json(self, data: Dict[str, Any]) -> None:
        try:
            with open(self.file_path, 'w', encoding='utf-8') as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=4)
            self.logger.info(f'Data successfully written to {self.file_path}.')
        except Exception as e:
            self.logger.error(f'Error writing JSON file: {e}')

    def update_json(self, updates: Dict[str, Any]) -> None:
        data = self.load_json()
        data.update(updates)
        self.write_json(data)

    def get_value(self, key: str) -> Any:
        data = self.load_json()
        return data.get(key)

    def delete_key(self, key: str) -> None:
        data = self.load_json()
        if key in data:
            del data[key]
            self.write_json(data)
            self.logger.info(f"Key '{key}' successfully removed.")
        else:
            self.logger.warning(f"Key '{key}' not found in JSON.")
