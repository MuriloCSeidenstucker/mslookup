import json
import logging

from datetime import datetime
from typing import Dict, List
from logger_config import main_logger

class PDFProcessingService:
    def __init__(self, pdf_manager, anvisa_domain, report_generator):
        self.logger = logging.getLogger(f'main_logger.{self.__class__.__name__}')
        self.pdf_manager = pdf_manager
        self.anvisa_domain = anvisa_domain
        self.report_generator = report_generator
    
    def process_candidate_pdfs(self, candidate_data):
        reg_data = {}
        for candidate in candidate_data:
            if candidate['reg_candidates']:
                first_reg = candidate['reg_candidates'][0]
                if first_reg['register'] == 26:
                    pass
                has_pdf_in_db = self.pdf_manager.get_pdf_in_db(first_reg['register'], candidate['concentration'])
                registration_obtained = False
                if not has_pdf_in_db:
                    registration_obtained = self.anvisa_domain.get_register_as_pdf(
                        first_reg['register'],
                        candidate['concentration'],
                        first_reg['expiration_date'],
                        reg_data
                    )
                    if registration_obtained:
                        self.pdf_manager.copy_and_rename_file(
                            first_reg['register'],
                            first_reg['expiration_date']
                    )
                
                has_pdf = False
                if has_pdf_in_db or registration_obtained:
                    has_pdf = self.pdf_manager.rename_downloaded_pdf(f'Item {candidate["item"]}')
                    
                self.report_generator.add_entry({
                    'Item': candidate['item'],
                    'Descrição': candidate['description'],
                    'Concentração_Obtida': candidate['concentration'],
                    'Laboratório': candidate['laboratory'],
                    'Registro': first_reg['register'] if first_reg['register'] != -1 else 'Não encontrado',
                    'PDF': 'OK' if has_pdf else 'Pendente',
                })
            else:
                self.report_generator.add_entry({
                    'Item': candidate['item'],
                    'Descrição': candidate['description'],
                    'Concentração_Obtida': candidate['concentration'],
                    'Laboratório': candidate['laboratory'],
                    'Registro': 'Não encontrado',
                    'PDF': 'Pendente',
                })
        self.generate_json_file(reg_data, 'pdf_db.json')
                
    def generate_report(self):
        self.report_generator.generate_report()
        
    def generate_json_file(self, data: Dict[str, Dict[str, List[str]]], filename: str) -> None:
        try:
            existing_data = {}
            try:
                with open(filename, 'r', encoding='utf-8') as file:
                    existing_data = json.load(file)
            except FileNotFoundError:
                pass

            for key, value in data.items():
                if key not in existing_data:
                    existing_data[key] = value
                else:
                    updated_presentations = set(existing_data[key]['presentations']).union(set(value['presentations']))
                    existing_data[key]['presentations'] = list(updated_presentations)
                    
                    existing_expiration_date = datetime.strptime(existing_data[key]['expiration_date'], '%d/%m/%Y')
                    new_expiration_date = datetime.strptime(value['expiration_date'], '%d/%m/%Y')
                    if new_expiration_date > existing_expiration_date:
                        existing_data[key]['expiration_date'] = value['expiration_date']

            with open(filename, 'w', encoding='utf-8') as file:
                json.dump(existing_data, file, ensure_ascii=False, indent=4)
            self.logger.info(f'JSON file successfully generated: "{filename}"')
        except (IOError, TypeError) as e:
            self.logger.error(f"Failed to generate JSON file '{filename}': {e}")
            raise