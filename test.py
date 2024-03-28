import pandas as pd
from data_processor import DataProcessor
from search_in_open_data_anvisa import OpenDataAnvisa
from access_anvisa_domain import AnvisaDomain

anvisa_domain = AnvisaDomain()
anvisa_domain.get_register_as_pdf('102350779')

# file_path = r"C:\Users\dell\OneDrive\Área de Trabalho\Itens_Errados.xlsx"
# item_col = 'Item'
# desc_col = 'Descrição'
# brand_col = 'Marca'

# data_processor = DataProcessor(file_path)
# data = data_processor.get_data(item_col, desc_col, brand_col)

# report_data = []
# # instance = SearchAndPrint()
# instance = OpenDataAnvisa()
# for entry in data:
#     register = instance.get_register(entry['item'], entry['description'], entry['brand'])
#     # success = instance.get_register_as_pdf(entry['item'], entry['description'], entry['brand'])
#     report_data.append({'Item': entry['item'],
#                         'Descrição': entry['description'],
#                         'Marca': entry['brand'] if isinstance(entry['brand'], str) else entry['brand']['Name'],
#                         'Registro': register if register != -1 else 'Não encontrado'
#                         })

# report_df = pd.DataFrame(report_data)
# report_df.to_excel('relatorio_registros_errados.xlsx', index=False)