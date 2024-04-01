import os
import time
import pandas as pd
from search_in_smerp import SearchInSmerp
from search_in_open_data_anvisa import OpenDataAnvisa
from access_anvisa_domain import AnvisaDomain
from data_processor import DataProcessor
from utils import Utils

class Program:
    
    def rename_downloaded_pdf(path, new_name):
        # Lista todos os arquivos na pasta de downloads
        files = os.listdir(path)
        
        # Procura pelo arquivo PDF com o nome padrão
        pdf_file = None
        for file in files:
            if (file.startswith('Consultas - Agência Nacional de Vigilância Sanitária') and
                file.endswith('.pdf')):
                pdf_file = file
                break
        
        if pdf_file:
            # Constrói o caminho completo para o arquivo PDF
            old_path = os.path.join(path, pdf_file)
            
            # Constrói o novo caminho com o novo nome
            new_path = os.path.join(path, new_name + '.pdf')
            
            # Renomeia o arquivo
            os.rename(old_path, new_path)
            print(f"Arquivo PDF renomeado para '{new_name}.pdf'")
        else:
            print("Nenhum arquivo PDF com o nome padrão encontrado na pasta de downloads.")

    start_time = time.time()

    # file_path = r"D:\Documents\Pregoes_Eletr\DM\Cadastrados\PE_112024_Campina-Verde\Controle_Operacao_PE_112024_Campina-Verde.xlsm"
    file_path = r"D:\Documents\Pregoes_Eletr\DM\Finalizado\PE_042024_Frutal\Controle_Operacao_PE_042024_Frutal.xlsm"
    item_col = 'ITEM'
    desc_col = 'DESCRIÇÃO'
    brand_col = 'MARCA'

    data_processor = DataProcessor(file_path)
    data = data_processor.get_data(item_col, desc_col, brand_col)
    
    d_path = r"C:\Users\dell\Downloads"

    report_data = []
    smerp_search = SearchInSmerp()
    data_anvisa_search = OpenDataAnvisa()
    anvisaDomain = AnvisaDomain()
    for entry in data:
        process_number = None
        register = data_anvisa_search.get_register(entry['item'], entry['description'], entry['brand'])
        if register == -1:
            register, process_number = smerp_search.get_data_from_smerp(entry['item'], entry['description'], entry['brand'])
        if register != -1:
            anvisaDomain.get_register_as_pdf(register, process_number)
            rename_downloaded_pdf(d_path, f'Item {entry['item']}')
        report_data.append({'Item': entry['item'],
                            'Descrição': entry['description'],
                            'Marca': entry['brand'] if isinstance(entry['brand'], str) else entry['brand']['Name'],
                            'Registro': register if register != -1 else 'Não encontrado'
                            })

    report_df = pd.DataFrame(report_data)
    report_df.to_excel('relatorio_registros.xlsx', index=False)
    
    end_time = time.time()
    elapsed_time  = Utils.calculate_elapsed_time(start_time, end_time)
    print(f'Tempo decorrido: {elapsed_time}')
    