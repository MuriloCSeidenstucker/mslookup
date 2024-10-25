import os
import logging
from datetime import datetime
from pathlib import Path
import sys

def configure_logging():
    # Criação do manipulador de log rotativo com base na data
    date = datetime.now().strftime("%d-%m-%Y")
    file_name = f"{date}_logs.log"
    log_dir = 'logs'  # Diretório para os arquivos de log
    full_file_path = os.path.join(log_dir, file_name)
    
    # Cria o diretório se não existir
    os.makedirs(log_dir, exist_ok=True)
    
    # Configuração do FileHandler com codificação 'utf-8'
    file_handler = logging.FileHandler(full_file_path, mode='a', encoding='utf-8')
    
    # Define os padrões do Log
    logging.basicConfig(
        level=logging.INFO,
        encoding="utf-8",
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%d-%m-%Y %H:%M:%S",
        handlers=[
            file_handler,
            logging.StreamHandler(),
        ],
    )
    
def configure_test_logging():
    # Criação do manipulador de log rotativo com base na data
    date = datetime.now().strftime("%d-%m-%Y")
    file_name = f"{date}_test_logs.log"
    log_dir = r'logs\test'  # Diretório para os arquivos de log
    full_file_path = os.path.join(log_dir, file_name)
    
    # Cria o diretório se não existir
    os.makedirs(log_dir, exist_ok=True)
    
    # Configuração do FileHandler com codificação 'utf-8'
    file_handler = logging.FileHandler(full_file_path, mode='a', encoding='utf-8')
    
    # Define os padrões do Log
    logging.basicConfig(
        level=logging.INFO,
        encoding="utf-8",
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%d-%m-%Y %H:%M:%S",
        handlers=[
            file_handler,
            logging.StreamHandler(),
        ],
    )
    
def base_path( file_path: str):
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return Path(f'{sys._MEIPASS}/{file_path}')
    return Path(file_path)