import os
import re
import shutil
import logging

from datetime import datetime
from logger_config import main_logger

class PDFManager:
    def __init__(self):
        self.DOWNLOAD_PATH = os.path.join(os.path.expanduser('~'), 'Downloads')
        self.logger = logging.getLogger(f'main_logger.{self.__class__.__name__}')
    
    def get_pdf_in_db(self, target_reg: str) -> bool:
        if not isinstance(target_reg, str):
            self.logger.error(f'Invalid input type for target_reg: {type(target_reg)}')
            return False
        
        pattern = r'(\d{9})_(\d{2}-\d{2}-\d{4})'
        path = 'registers_pdf'
        
        try:
            files = os.listdir(path)
        except OSError as e:
            self.logger.error(f'Error listing directory {path}: {e}')
            return False

        for file in files:
            file_path = os.path.join(path, file)
            
            if os.path.isfile(file_path):
                match = re.match(pattern, file)
                
                if match:
                    expiration_date = match.group(2)
                    register = match.group(1)
                        
                    if int(target_reg) == int(register):
                        try:
                            dt = datetime.strptime(expiration_date, '%d-%m-%Y')
                        except ValueError as e:
                            self.logger.error(f'Error parsing date {expiration_date}: {e}')
                            continue
                        
                        if dt < datetime.now():
                            self.logger.warning(f'{file} is expired')
                            return False
                        
                        new_file_name = 'Consultas - Agência Nacional de Vigilância Sanitária.pdf'
                        destination_path = os.path.join(self.DOWNLOAD_PATH, new_file_name)
                        
                        try:
                            shutil.copy2(file_path, destination_path)
                        except Exception as e:
                            self.logger.error(f'Error copying file {file_path} to {destination_path}: {e}')
                            return False
                        
                        self.logger.info(f'Registration: {target_reg} found in {file}')
                        return True
                    
        self.logger.info(f'Registration {target_reg} not found in database')
        return False
    
    def copy_and_rename_file(self, register: str, expiration_date: str) -> None:
        if not isinstance(register, str) or not isinstance(expiration_date, str):
            self.logger.error('Invalid input types for register or expiration_date')
            return
        
        exp_date_formatted = expiration_date.replace('/', '-') if expiration_date != '-1' else 'no-date'
        target_path = 'registers_pdf'
        searched_file_name = "Consultas - Agência Nacional de Vigilância Sanitária.pdf"

        if os.path.exists(self.DOWNLOAD_PATH):
            try:
                files = os.listdir(self.DOWNLOAD_PATH)
            except Exception as e:
                self.logger.error(f'Error listing directory {self.DOWNLOAD_PATH}: {e}')
                return
            
            for file in files:
                file_path = os.path.join(self.DOWNLOAD_PATH, file)
                
                if os.path.isfile(file_path) and file == searched_file_name:
                    new_file_name = f'{register}_{exp_date_formatted}.pdf'
                    destination_path = os.path.join(target_path, new_file_name)
                    
                    try:
                        shutil.copy2(file_path, destination_path)
                    except Exception as e:
                        self.logger.error(f'Error copying file {file_path} to {destination_path}: {e}')
                        return
                    
                    self.logger.info("File successfully copied and renamed.")
                    break
            else:
                self.logger.warning("No file with the searched name was found.")
        else:
            self.logger.error("The specified source directory does not exist.")

    def rename_downloaded_pdf(self, new_name: str) -> bool:
        if not isinstance(new_name, str):
            self.logger.error(f'Invalid input type for new_name: {type(new_name)}')
            return False
        
        try:
            files = os.listdir(self.DOWNLOAD_PATH)
        except Exception as e:
            self.logger.error(f'Error listing directory {self.DOWNLOAD_PATH}: {e}')
            return False
        
        pdf_file = None
        
        for file in files:
            if (file.startswith('Consultas - Agência Nacional de Vigilância Sanitária') and
                file.endswith('.pdf')):
                pdf_file = file
                break
        
        if pdf_file:
            old_path = os.path.join(self.DOWNLOAD_PATH, pdf_file)
            new_path = os.path.join(self.DOWNLOAD_PATH, new_name + '.pdf')
            
            if os.path.exists(new_path):
                base_name, ext = os.path.splitext(new_path)
                i = 1
                while True:
                    new_path = os.path.join(self.DOWNLOAD_PATH, f"{base_name} ({i}){ext}")
                    if not os.path.exists(new_path):
                        break
                    i += 1
                    
            try:
                os.rename(old_path, new_path)
            except Exception as e:
                self.logger.error(f'Error renaming file {old_path} to {new_path}: {e}')
                return False
            
            self.logger.info("File successfully renamed.")
            return True
        else:
            self.logger.warning("No PDF file with the standard name found in the downloads folder.")
            return False
