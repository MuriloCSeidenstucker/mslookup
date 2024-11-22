
from typing import Any, Dict, List

import pandas as pd

from mslookup.app.logger_config import get_logger


class ReportGenerator:
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        
        self.logger.info('Instantiated.')
        
        self.report_data: List[Dict[str, Any]] = []
        self.entry_count = 0

    def add_entry(self, entry: Dict[str, Any]) -> None:
        self.entry_count += 1
        if not isinstance(entry, dict):
            self.logger.error(
                f'Item {self.entry_count}: Invalid entry type: {type(entry)}. Expected a dictionary.'
            )
            raise ValueError('Entry must be a dictionary')

        for key, value in entry.items():
            if not isinstance(key, str):
                self.logger.error(
                    f'Item {self.entry_count}: Invalid key type: {type(key)}. Expected a string.'
                )
                raise ValueError(f'Key must be a string, got {type(key)}')

        self.report_data.append(entry)

    def generate_report(
        self,
        report_data: List[Dict[str, Any]],
        filename: str = 'relatorio_registros.xlsx',
    ) -> None:
        self.logger.info('Starting execution.')
        if not filename.endswith('.xlsx'):
            self.logger.error(
                f'Invalid file extension: {filename}. Expected a .xlsx file.'
            )
            raise ValueError('Filename must end with .xlsx')

        try:
            report_df = pd.DataFrame(report_data)
            report_df.to_excel(filename, index=False)
            self.logger.info(f'Report successfully generated: {filename}')
            self.logger.info('Execution completed.')
        except Exception as e:
            self.logger.error(f'Failed to generate report: {e}')
            raise ValueError(f'Failed to generate report: {e}')
