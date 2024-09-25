import logging
import os
import re
import shutil
from datetime import datetime
from typing import List

from src.json_manager import JsonManager
from src.utils import Utils


class PDFManager:
    def __init__(self):
        self.DOWNLOAD_PATH = os.path.join(os.path.expanduser('~'), 'Downloads')
        self.STANDARD_NAME = (
            'Consultas - Agência Nacional de Vigilância Sanitária.pdf'
        )
        self.logger = logging.getLogger(
            f'main_logger.{self.__class__.__name__}'
        )

        self.json_manager = JsonManager(r'data\resources\pdf_db.json')
        self.db = self.json_manager.load_json()

    def get_pdf_in_db(
        self, target_reg: str, concentration: str, data_updated: bool
    ) -> bool:
        if not isinstance(target_reg, str):
            self.logger.error(
                f'Invalid input type for target_reg: {type(target_reg)}'
            )
            return False

        if data_updated:
            self.db = self.json_manager.load_json()

        path = r'data\registers_pdf'

        if target_reg not in self.db:
            self.logger.info(
                f'Registration {target_reg} not found in database'
            )
            return False

        expiration_date = self.db[target_reg]['expiration_date']
        presentations = self.db[target_reg]['presentations']

        try:
            if isinstance(expiration_date, str):
                exp_date = datetime.strptime(expiration_date, '%d/%m/%Y')
            elif isinstance(expiration_date, int):
                exp_date = datetime(1970, 1, 1)
            else:
                raise ValueError('Invalid expiration date format')
        except ValueError as e:
            self.logger.error(f'Error parsing date {expiration_date}: {e}')
            return False

        if exp_date < datetime.now():
            self.logger.warning(f'Registration {target_reg} is expired')
            return False

        if not self.verify_concentration(concentration, presentations):
            return False

        try:
            files = os.listdir(path)
        except OSError as e:
            self.logger.error(f'Error listing directory {path}: {e}')
            return False

        for file in files:
            file_path = os.path.join(path, file)

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
                        self.logger.error(
                            f'Error copying file {file_path} to {destination_path}: {e}'
                        )
                        return False

                    self.logger.info(
                        f'Registration: {target_reg} found in database as {file}'
                    )
                    return True

        self.logger.info(f'Registration {target_reg} not found in directory')
        return False

    def verify_concentration(
        self, concentration: str, presentations: List[str]
    ) -> bool:
        try:
            match = any(
                Utils.remove_accents_and_spaces(concentration)
                in Utils.remove_accents_and_spaces(presentation)
                for presentation in presentations
            )

            if match:
                return True
            else:
                self.logger.warning('Concentration found does not match')
                return False
        except Exception as e:
            self.logger.error(f'Error verifying concentration: {e}')
            return False

    def copy_and_rename_file(
        self, register: str, expiration_date: str
    ) -> None:
        if not isinstance(register, str) or not isinstance(
            expiration_date, str
        ):
            self.logger.error(
                f'Invalid input types for register:{type(register)} or expiration_date:{type(expiration_date)}'
            )
            return

        exp_date_formatted = (
            expiration_date.replace('/', '-')
            if expiration_date != '-1'
            else 'no-date'
        )
        target_path = r'data\registers_pdf'
        searched_file_name = self.STANDARD_NAME

        if os.path.exists(self.DOWNLOAD_PATH):
            try:
                files = os.listdir(self.DOWNLOAD_PATH)
            except Exception as e:
                self.logger.error(
                    f'Error listing directory {self.DOWNLOAD_PATH}: {e}'
                )
                return

            file_found = False
            for file in files:
                file_path = os.path.join(self.DOWNLOAD_PATH, file)

                if os.path.isfile(file_path) and file == searched_file_name:
                    new_file_name = f'{register}_{exp_date_formatted}.pdf'
                    destination_path = os.path.join(target_path, new_file_name)

                    try:
                        shutil.copy2(file_path, destination_path)
                    except Exception as e:
                        self.logger.error(
                            f'Error copying file {file_path} to {destination_path}: {e}'
                        )
                        return

                    self.logger.info(
                        f'File successfully copied and renamed to database: {new_file_name}'
                    )
                    file_found = True
                    break

            if not file_found:
                self.logger.warning(
                    f'{self.copy_and_rename_file.__name__}: No PDF file with the standard name found in {self.DOWNLOAD_PATH}'
                )
        else:
            self.logger.error('The specified source directory does not exist.')

    def rename_downloaded_pdf(self, new_name: str) -> bool:
        if not isinstance(new_name, str):
            self.logger.error(
                f'Invalid input type for new_name: {type(new_name)}'
            )
            return False

        try:
            files = os.listdir(self.DOWNLOAD_PATH)
        except Exception as e:
            self.logger.error(
                f'Error listing directory {self.DOWNLOAD_PATH}: {e}'
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
                self.logger.error(
                    f'Error renaming file {old_path} to {new_path}: {e}'
                )
                return False

            self.logger.info(f'File successfully renamed to {new_path}')
            return True
        else:
            self.logger.warning(
                f'{self.rename_downloaded_pdf.__name__}: No PDF file with the standard name found in {self.DOWNLOAD_PATH}'
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

            self.logger.info(
                f'Failed to print the file as PDF. Not found in "{root}"'
            )
            return False
        except Exception as e:
            self.logger.error(f'An error occurred: {e}')
            return False
