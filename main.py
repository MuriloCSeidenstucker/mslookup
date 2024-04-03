import time
import pandas as pd
from search_in_smerp import SearchInSmerp
from search_in_open_data_anvisa import OpenDataAnvisa
from access_anvisa_domain import AnvisaDomain
from data_processor import DataProcessor
from utils import Utils

class Program:
    
    start_time = time.time()

    # file_path = r"D:\Documents\Pregoes_Eletr\DM\Cadastrados\PE_112024_Campina-Verde\Controle_Operacao_PE_112024_Campina-Verde.xlsm"
    # file_path = r"D:\Documents\Pregoes_Eletr\DM\Finalizado\PE_042024_Frutal\Controle_Operacao_PE_042024_Frutal.xlsm"
    file_path = r"D:\Documents\Pregoes_Eletr\DM\Cadastrados\PE_090092024_Araxa\Controle_Operacao_PE_090092024_Araxa.xlsm"
    item_col = 'ITEM'
    desc_col = 'DESCRIÇÃO'
    brand_col = 'MARCA'

    processor_start_time = time.time()
    data_processor = DataProcessor(file_path)
    data = data_processor.get_data(item_col, desc_col, brand_col)
    processor_end_time = time.time()
    processor_elapsed_time = Utils.calculate_elapsed_time(processor_start_time, processor_end_time)
    
    d_path = r"C:\Users\dell\Downloads"

    report_data = []
    smerp_search = SearchInSmerp()
    data_anvisa_search = OpenDataAnvisa()
    anvisaDomain = AnvisaDomain()
    anvisa_search_start_time = time.time()
    for entry in data:
        process_number = None
        register = data_anvisa_search.get_register(entry['item'], entry['description'], entry['brand'])
        if register == -1:
            register, process_number = smerp_search.get_data_from_smerp(entry['item'], entry['description'], entry['brand'])
        if register != -1:
            anvisaDomain.get_register_as_pdf(register, process_number)
            Utils.rename_downloaded_pdf(d_path, f'Item {entry['item']}')
        report_data.append({'Item': entry['item'],
                            'Descrição': entry['description'],
                            'Marca': entry['brand'] if isinstance(entry['brand'], str) else entry['brand']['Name'],
                            'Registro': register if register != -1 else 'Não encontrado'
                            })
    anvisa_search_end_time = time.time()
    anvisa_search_elapsed_time = Utils.calculate_elapsed_time(anvisa_search_start_time, anvisa_search_end_time)

    report_df = pd.DataFrame(report_data)
    report_df.to_excel('relatorio_registros.xlsx', index=False)
    
    end_time = time.time()
    elapsed_time  = Utils.calculate_elapsed_time(start_time, end_time)
    print(f'Tempo para processar dados: {processor_elapsed_time}')
    print(f'Tempo para obter registros: {anvisa_search_elapsed_time}')
    print(f'Tempo total decorrido: {elapsed_time}')
    