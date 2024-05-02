import os
import time
import pandas as pd
from search_in_smerp import SearchInSmerp
from search_in_open_data_anvisa import OpenDataAnvisa
from access_anvisa_domain import AnvisaDomain
from data_processor import DataProcessor
from utils import Utils

start_time = time.time()

file_path = r"data_for_testing\Controle_Operacao_PE_090092024_Araxa.xlsm"
item_col = 'ITEM'
desc_col = 'DESCRIÇÃO'
brand_col = 'MARCA'

processor_start_time = time.time()
# data_processor = DataProcessor(file_path)
data = [
    {
        'item': '1', 'description': 'ACETATO DE MEDROXIPROGESTERONA', "brand": 'cellera'
    },
    {
        'item': '2', 'description': 'aciclovir', "brand": 'cimed'
    }
]
processor_end_time = time.time()
processor_elapsed_time = Utils.calculate_elapsed_time(processor_start_time, processor_end_time)

d_path = os.path.join(os.path.expanduser('~'), 'Downloads')

smerp_search = SearchInSmerp()
data_anvisa_search = OpenDataAnvisa()
anvisaDomain = AnvisaDomain()

anvisa_search_start_time = time.time()
for i, entry in enumerate(data):
    s_time = time.time()
    print(f'\nTentando obter registro do item {i+1}/{len(data)}')
    process_number = None
    has_pdf = False
    register, process_number = smerp_search.get_data_from_smerp(entry['item'], entry['description'], entry['brand'])
    
anvisa_search_end_time = time.time()
anvisa_search_elapsed_time = Utils.calculate_elapsed_time(anvisa_search_start_time, anvisa_search_end_time)

end_time = time.time()
elapsed_time  = Utils.calculate_elapsed_time(start_time, end_time)
print(f"Quantidade de itens analizados: {len(data)}")
print(f'Tempo para processar dados: {processor_elapsed_time}')
print(f'Tempo para obter registros: {anvisa_search_elapsed_time}')
print(f'Tempo total decorrido: {elapsed_time}')
    