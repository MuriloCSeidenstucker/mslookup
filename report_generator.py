import logging
import pandas as pd

from typing import Any, Dict, List
from logger_config import main_logger

class ReportGenerator:
    def __init__(self):
        self.report_data: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(f'main_logger.{self.__class__.__name__}')
        self.entry_count = 0
    
    def add_entry(self, entry: Dict[str, Any]) -> None:
        self.entry_count += 1
        if not isinstance(entry, dict):
            self.logger.error(f"Item {self.entry_count}: Invalid entry type: {type(entry)}. Expected a dictionary.")
            raise ValueError("Entry must be a dictionary")
        
        for key, value in entry.items():
            if not isinstance(key, str):
                self.logger.error(f"Item {self.entry_count}: Invalid key type: {type(key)}. Expected a string.")
                raise ValueError(f"Key must be a string, got {type(key)}")
        
        self.report_data.append(entry)
        self.logger.info(f"Item {self.entry_count}: Entry successfully added")
    
    def generate_report(self, filename: str = 'relatorio_registros.xlsx') -> None:
        if not filename.endswith('.xlsx'):
            self.logger.error(f"Invalid file extension: {filename}. Expected a .xlsx file.")
            raise ValueError("Filename must end with .xlsx")
        
        try:
            report_df = pd.DataFrame(self.report_data)
            report_df.to_excel(filename, index=False)
            self.logger.info(f"Report successfully generated: {filename}")
        except Exception as e:
            self.logger.error(f"Failed to generate report: {e}")
            raise
