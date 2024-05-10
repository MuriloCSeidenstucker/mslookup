import os
import time
import pandas as pd

from utils import Utils
from pdf_manager import PDFManager
from data_processor import DataProcessor
from search_in_smerp import SearchInSmerp
from access_anvisa_domain import AnvisaDomain
from search_in_open_data_anvisa import OpenDataAnvisa

class Program:
    start_time = time.time()

    # file_path = r"data_for_testing\Controle_Operacao_PE_112024_Campina-Verde.xlsm"
    # file_path = r"data_for_testing\Controle_Operacao_PE_042024_Frutal.xlsm"
    file_path = r"data_for_testing\Controle_Operacao_PE_090092024_Araxa.xlsm"
    # file_path = r"data_for_testing\Itens_Errados.xlsx"
    item_col = 'ITEM'
    desc_col = 'DESCRIÇÃO'
    brand_col = 'MARCA'

    processor_start_time = time.time()
    data_processor = DataProcessor(file_path)
    data = data_processor.get_data(item_col, desc_col, brand_col)
    processor_end_time = time.time()
    processor_elapsed_time = Utils.calculate_elapsed_time(processor_start_time, processor_end_time)
    
    d_path = os.path.join(os.path.expanduser('~'), 'Downloads')

    report_data = []
    smerp_search = SearchInSmerp()
    data_anvisa_search = OpenDataAnvisa()
    anvisaDomain = AnvisaDomain()
    pdfManager = PDFManager()

    anvisa_search_start_time = time.time()
    for i, entry in enumerate(data):
        s_time = time.time()
        print(f'\nTentando obter registro do item {i+1}/{len(data)}')
        process_number = None
        expiration_date = None
        has_pdf = False
        register, expiration_date = data_anvisa_search.get_register(entry['item'], entry['description'], entry['brand'])
        if register == -1:
            register, process_number, expiration_date = smerp_search.get_data_from_smerp(entry['item'], entry['description'], entry['brand'])
        if register != -1:
            has_pdf_in_db = pdfManager.get_pdf_in_db(register)
            
            if not has_pdf_in_db:
                anvisaDomain.get_register_as_pdf(register, process_number)
                pdfManager.copy_and_rename_file(d_path, register, expiration_date)
                
            has_pdf = Utils.rename_downloaded_pdf(d_path, f'Item {entry['item']}')
            
        report_data.append({'Item': entry['item'],
                            'Descrição': entry['description'],
                            'Marca': entry['brand'] if isinstance(entry['brand'], str) else entry['brand']['Name'],
                            'Registro': register if register != -1 else 'Não encontrado',
                            'PDF': 'OK' if has_pdf else 'Pendente',
                            'Tempo Decorrido': Utils.calculate_elapsed_time(s_time, time.time())
                            })
        print(f'Resultado do item {i+1}/{len(data)}: Registro: {register if register != -1 else 'Não encontrado'}')
        print(f'PDF: {'OK' if has_pdf else 'Pendente'}')
        print(f'Tempo decorrido até o momento: {Utils.calculate_elapsed_time(start_time, time.time())}')
        
    anvisa_search_end_time = time.time()
    anvisa_search_elapsed_time = Utils.calculate_elapsed_time(anvisa_search_start_time, anvisa_search_end_time)

    report_df = pd.DataFrame(report_data)
    report_df.to_excel('relatorio_registros.xlsx', index=False)

    end_time = time.time()
    elapsed_time  = Utils.calculate_elapsed_time(start_time, end_time)
    print(f"Quantidade de itens analizados: {len(data)}")
    print(f'Tempo para processar dados: {processor_elapsed_time}')
    print(f'Tempo para obter registros: {anvisa_search_elapsed_time}')
    print(f'Tempo total decorrido: {elapsed_time}')
    