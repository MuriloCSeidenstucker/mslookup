import pandas as pd
from search_in_smerp import SearchInSmerp
from search_in_open_data_anvisa import OpenDataAnvisa
from data_processor import DataProcessor

class Program:

    # file_path = r"D:\Documents\Pregoes_Eletr\DM\Finalizado\PE_09.1522023_Araxa\Modelo_PE_09.1522023_Araxa.xlsx"
    # file_path = r"D:\Documents\Pregoes_Eletr\DM\Em_Andamento\PE_132024_Uberaba\Controle_Operacao_PE_132024_Uberaba.xlsm"
    # file_path = r"D:\Documents\Pregoes_Eletr\DM\Em_Andamento\PE_282023_Araguari\Controle_Operacao_PE_282023_Araguari.xlsm"
    # item_col = 'LOTE'
    # desc_col = 'DESCRIÇÃO DO ITEM'
    
    file_path = r"D:\Documents\Pregoes_Eletr\DM\Cadastrar\PE_112024_Campina-Verde\Controle_Operacao_PE_112024_Campina-Verde.xlsm"
    item_col = 'ITEM'
    desc_col = 'DESCRIÇÃO'
    brand_col = 'MARCA'

    data_processor = DataProcessor(file_path)
    data = data_processor.get_data(item_col, desc_col, brand_col)
    
    report_data = []
    # instance = SearchAndPrint()
    instance = OpenDataAnvisa()
    for entry in data:
        register = instance.get_register(entry['item'], entry['description'], entry['brand'])
        # success = instance.get_register_as_pdf(entry['item'], entry['description'], entry['brand'])
        report_data.append({'Item': entry['item'],
                            'Descrição': entry['description'],
                            'Marca': entry['brand'],
                            'Registro': register if register != -1 else 'Não encontrado'
                            })
        
    report_df = pd.DataFrame(report_data)
    report_df.to_excel('relatorio_registros.xlsx', index=False)

    # instance = SearchAndPrint()
    # instance.get_register_as_pdf('2', 'ACETILCISTEÍNA, DOSAGEM 100 MG, INDICAÇÃO PÓ PARA SOLUÇÃO ORAL', 'Eurofarma')
    