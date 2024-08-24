import json
import logging

from datetime import datetime
from typing import Dict, List

from pdf_manager import PDFManager
from logger_config import main_logger
from report_generator import ReportGenerator
from access_anvisa_domain import AnvisaDomain

class PDFProcessingService:
    def __init__(self, pdf_manager: PDFManager, anvisa_domain: AnvisaDomain, report_generator: ReportGenerator):
        self.logger = logging.getLogger(f'main_logger.{self.__class__.__name__}')
        self.pdf_manager = pdf_manager
        self.anvisa_domain = anvisa_domain
        self.report_generator = report_generator
    
    def process_candidate_pdfs(self, candidate_data):
        reg_data = {}
        data_updated = False
        
        for candidate in candidate_data:
                        
            data_modified = False
            
            if candidate['reg_candidates']:
                for i, reg in enumerate(candidate['reg_candidates']):
                    has_pdf_in_db = self.pdf_manager.get_pdf_in_db(reg['register'], candidate['concentration'], data_updated)
                    
                    registration_obtained = False
                    if not has_pdf_in_db:
                        registration_obtained = self.anvisa_domain.get_register_as_pdf(
                            reg['register'],
                            candidate['concentration'],
                            reg['expiration_date'],
                            reg_data
                        )
                        if registration_obtained:
                            data_modified = True
                            self.pdf_manager.copy_and_rename_file(
                                reg['register'],
                                reg['expiration_date']
                            )
                    
                    has_pdf = False
                    if has_pdf_in_db or registration_obtained:
                        has_pdf = self.pdf_manager.rename_downloaded_pdf(f'Item {candidate["item"]}')
                        
                    if has_pdf:
                        self.report_generator.add_entry({
                            'Item': candidate['item'],
                            'Descrição': candidate['origin_description'],
                            'Concentração_Encontrada': candidate['concentration'],
                            'Laboratório': candidate['laboratory'],
                            'Registro': reg['register'] if reg['register'] != -1 else 'Não encontrado',
                            'PDF': 'OK' if has_pdf else 'Pendente',
                        })
                        break
                        
                    if i == len(candidate['reg_candidates']) - 1:
                        self.report_generator.add_entry({
                            'Item': candidate['item'],
                            'Descrição': candidate['origin_description'],
                            'Concentração_Encontrada': candidate['concentration'],
                            'Laboratório': candidate['laboratory'],
                            'Registro': f'Último registro encontrado: {reg['register']}' if reg['register'] != -1 else 'Não encontrado',
                            'PDF': 'OK' if has_pdf else 'Pendente',
                        })
            else:
                self.report_generator.add_entry({
                    'Item': candidate['item'],
                    'Descrição': candidate['origin_description'],
                    'Concentração_Encontrada': candidate['concentration'],
                    'Laboratório': candidate['laboratory'],
                    'Registro': 'Não encontrado',
                    'PDF': 'Pendente',
                })
                
            if data_modified:
                self.generate_json_file(reg_data, 'pdf_db.json')
                data_updated = True
            else:
                data_updated = False
        
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
                    
                    existing_exp_date_str = existing_data[key]['expiration_date']
                    new_exp_date_str = value['expiration_date']
                    
                    if (isinstance(existing_exp_date_str, str) and
                        existing_exp_date_str != 'nan' and
                        existing_exp_date_str != 'DATA INVÁLIDA'):
                        existing_expiration_date = datetime.strptime(existing_exp_date_str, '%d/%m/%Y')
                    else:
                        existing_expiration_date = datetime.min
                    
                    if isinstance(new_exp_date_str, str) and new_exp_date_str != 'nan':
                        new_expiration_date = datetime.strptime(new_exp_date_str, '%d/%m/%Y')
                    else:
                        new_expiration_date = datetime.min
                    
                    if new_expiration_date > existing_expiration_date:
                        existing_data[key]['expiration_date'] = value['expiration_date']

            with open(filename, 'w', encoding='utf-8') as file:
                json.dump(existing_data, file, ensure_ascii=False, indent=4)
            self.logger.info(f'JSON file successfully generated: "{filename}"')
        except (IOError, TypeError) as e:
            self.logger.error(f"Failed to generate JSON file '{filename}': {e}")
            raise