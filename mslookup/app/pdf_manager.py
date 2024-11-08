import logging
import os
from pathlib import Path
import re
import shutil
from datetime import datetime
import sys
from typing import List, Optional, Tuple, Union

from mslookup.app.json_manager import JsonManager
from mslookup.app.logger_config import configure_logging
from mslookup.app.utils import Utils


class PDFManager:
    def __init__(self):
        configure_logging()
        self.name = self.__class__.__name__
        logging.info(f'{self.name}: Instantiated.')
        
        self.DOWNLOAD_PATH = os.path.join(os.path.expanduser('~'), 'Downloads')
        self.STANDARD_NAME = (
            'Consultas - Agência Nacional de Vigilância Sanitária.pdf'
        )
        self.json_manager = JsonManager(r'data\resources\pdf_db.json')
        self.db = self.json_manager.load_json()
        self.register_path = self.base_path(r'data\registers_pdf')
        
    def base_path(self, file_path: str):
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            return Path(f'{sys._MEIPASS}/{file_path}')
        return Path(file_path)

    def get_pdf_in_db(
        self, target_reg: str, concentration: str, data_updated: bool
    ) -> bool:
        presentation = None
        if not isinstance(target_reg, str):
            logging.error(
                f'{self.name}: Invalid input type for target_reg: {type(target_reg)}'
            )
            return False, presentation

        if data_updated:
            self.db = self.json_manager.load_json()

        if target_reg not in self.db:
            return False, presentation

        expiration_date = self.db[target_reg]['expiration_date']
        presentations = self.db[target_reg]['presentations']

        try:
            if isinstance(expiration_date, str):
                exp_date = datetime.strptime(expiration_date, '%d/%m/%Y')
            elif isinstance(expiration_date, int):
                exp_date = datetime(1970, 1, 1)
            else:
                logging.error(f'{self.name}: Invalid expiration date format.')
                raise ValueError('Invalid expiration date format')
        except ValueError as e:
            logging.error(f'{self.name}: Error parsing date {expiration_date}: {e}')
            return False, presentation

        if exp_date < datetime.now():
            logging.warning(f'{self.name}: Registration {target_reg} is expired')
            return False, presentation

        concentrationFound, presentation = self.verify_concentration(concentration, presentations)
        if not concentrationFound:
            return False, presentation

        try:
            files = os.listdir(self.register_path)
        except OSError as e:
            logging.error(f'{self.name}: Error listing directory {self.register_path}: {e}')
            return False, presentation

        for file in files:
            file_path = os.path.join(self.register_path, file)

            if os.path.isfile(file_path):
                pattern = rf'{target_reg}_\d{{2}}-\d{{2}}-\d{{4}}'
                if re.match(pattern, file):
                    new_file_name = self.STANDARD_NAME
                    destination_path = os.path.join(
                        self.DOWNLOAD_PATH, new_file_name
                    )

                    try:
                        shutil.copy2(file_path, destination_path)
                    except Exception as e:
                        logging.error(
                            f'{self.name}: Error copying file {file_path} to {destination_path}: {e}'
                        )
                        return False, presentation
                    return True, presentation
        return False, presentation

    def verify_concentration(
        self, concentration: str, presentations: List[str]
    )-> Union[bool, Tuple[bool, Optional[str]]]:
        try:
            for presentation in presentations:
                if Utils.remove_accents_and_spaces(concentration) in Utils.remove_accents_and_spaces(presentation):
                    return True, presentation

            logging.warning(f'{self.name}: Concentration found does not match')
            return False, None
        except Exception as e:
            logging.critical(f'{self.name}: Error verifying concentration: {e}')
            return False, None

    def copy_and_rename_file(
        self, register: str, expiration_date: str
    ) -> None:
        if not isinstance(register, str) or not isinstance(
            expiration_date, str
        ):
            logging.error(
                f'{self.name}: Invalid input types for register:{type(register)} or expiration_date:{type(expiration_date)}'
            )
            return

        exp_date_formatted = (
            expiration_date.replace('/', '-')
            if expiration_date != '-1'
            else 'no-date'
        )
        searched_file_name = self.STANDARD_NAME

        if os.path.exists(self.DOWNLOAD_PATH):
            try:
                files = os.listdir(self.DOWNLOAD_PATH)
            except Exception as e:
                logging.error(
                    f'{self.name}: Error listing directory {self.DOWNLOAD_PATH}: {e}'
                )
                return

            file_found = False
            for file in files:
                file_path = os.path.join(self.DOWNLOAD_PATH, file)

                if os.path.isfile(file_path) and file == searched_file_name:
                    new_file_name = f'{register}_{exp_date_formatted}.pdf'
                    destination_path = os.path.join(self.register_path, new_file_name)

                    os.makedirs(self.register_path, exist_ok=True)
                    try:
                        shutil.copy2(file_path, destination_path)
                    except Exception as e:
                        logging.error(
                            f'{self.name}: Error copying file {file_path} to {destination_path}: {e}'
                        )
                        return

                    file_found = True
                    break

            if not file_found:
                logging.warning(
                    f'{self.name}: No PDF file with the standard name found in {self.DOWNLOAD_PATH}'
                )
        else:
            logging.error(f'{self.name}: The specified source directory does not exist.')

    def rename_downloaded_pdf(self, new_name: str) -> bool:
        if not isinstance(new_name, str):
            logging.error(
                f'{self.name}: Invalid input type for new_name: {type(new_name)}'
            )
            return False

        try:
            files = os.listdir(self.DOWNLOAD_PATH)
        except Exception as e:
            logging.error(
                f'{self.name}: Error listing directory {self.DOWNLOAD_PATH}: {e}'
            )
            return False

        pdf_file = None

        for file in files:
            if file.startswith(
                'Consultas - Agência Nacional de Vigilância Sanitária'
            ) and file.endswith('.pdf'):
                pdf_file = file
                break

        if pdf_file:
            old_path = os.path.join(self.DOWNLOAD_PATH, pdf_file)
            new_path = os.path.join(self.DOWNLOAD_PATH, new_name + '.pdf')

            if os.path.exists(new_path):
                base_name, ext = os.path.splitext(new_path)
                i = 1
                while True:
                    new_path = os.path.join(
                        self.DOWNLOAD_PATH, f'{base_name} ({i}){ext}'
                    )
                    if not os.path.exists(new_path):
                        break
                    i += 1

            try:
                os.rename(old_path, new_path)
            except Exception as e:
                logging.error(
                    f'{self.name}: Error renaming file {old_path} to {new_path}: {e}'
                )
                return False
            return True
        else:
            logging.warning(
                f'{self.name}: No PDF file with the standard name found in {self.DOWNLOAD_PATH}'
            )
            return False

    def pdf_was_printed(self) -> bool:
        try:
            if not os.path.isdir(self.DOWNLOAD_PATH):
                raise ValueError(
                    f'The provided path "{self.DOWNLOAD_PATH}" is not a valid directory'
                )

            for root, dirs, files in os.walk(self.DOWNLOAD_PATH):
                if self.STANDARD_NAME in files:
                    return True

            logging.error(
                f'{self.name}: Failed to print the file as PDF. Not found in "{root}"'
            )
            return False
        except Exception as e:
            logging.critical(f'{self.name}: An error occurred: {e}')
            return False
