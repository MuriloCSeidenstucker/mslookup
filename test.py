import pandas as pd
from data_processor import DataProcessor
from search_in_smerp import SearchInSmerp
from search_in_open_data_anvisa import OpenDataAnvisa
from access_anvisa_domain import AnvisaDomain

file_path = r"D:\Documents\Pregoes_Eletr\DM\Cadastrados\PE_112024_Campina-Verde\Controle_Operacao_PE_112024_Campina-Verde.xlsm"
item_col = 'Item'
desc_col = 'Descrição'
brand_col = 'Marca'

data_processor = DataProcessor(file_path)
data = data_processor.get_data(item_col, desc_col, brand_col)

report_data = []
smerp_search = SearchInSmerp()
data_anvisa_search = OpenDataAnvisa()
for entry in data:
    register = data_anvisa_search.get_register(entry['item'], entry['description'], entry['brand'])
    if register == -1:
        register = smerp_search.get_data_from_smerp(entry['item'], entry['description'], entry['brand'])[0]
    report_data.append({'Item': entry['item'],
                        'Descrição': entry['description'],
                        'Marca': entry['brand'] if isinstance(entry['brand'], str) else entry['brand']['Name'],
                        'Registro': register if register != -1 else 'Não encontrado'
                        })

report_df = pd.DataFrame(report_data)
report_df.to_excel('relatorio_registros_errados.xlsx', index=False)