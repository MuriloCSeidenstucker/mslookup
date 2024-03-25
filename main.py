import pandas as pd
from search_and_print import SearchAndPrint
from data_processor import DataProcessor

class Program:

    # file_path = r"D:\Documents\Pregoes_Eletr\DM\Finalizado\PE_09.1522023_Araxa\Modelo_PE_09.1522023_Araxa.xlsx"
    # file_path = r"D:\Documents\Pregoes_Eletr\DM\Em_Andamento\PE_132024_Uberaba\Controle_Operacao_PE_132024_Uberaba.xlsm"
    # item_col = 'LOTE'
    # desc_col = 'DESCRIÇÃO DO ITEM'
    
    file_path = r"D:\Documents\Pregoes_Eletr\DM\Em_Andamento\PE_282023_Araguari\Controle_Operacao_PE_282023_Araguari.xlsm"
    item_col = 'ITEM'
    desc_col = 'DESCRIÇÃO'
    brand_col = 'MARCA'

    data_processor = DataProcessor(file_path)
    data = data_processor.get_data(item_col, desc_col, brand_col)

    report_data = []
    instance = SearchAndPrint()
    for entry in data:
        print(entry['brand'])
        # success = instance.get_register_as_pdf(entry['item'], entry['description'], entry['brand'])
        # report_data.append({'Item': entry['item'],
        #                     'Descrição': entry['description'],
        #                     'Marca': entry['brand'],
        #                     'Registro': 'Sucesso' if success else 'Falha'
                            # })
        
    # report_df = pd.DataFrame(report_data)
    # report_df.to_excel('relatorio_registros.xlsx', index=False)

    # instance = SearchAndPrint()
    # instance.get_register_as_pdf('2', 'ACETILCISTEÍNA, DOSAGEM 100 MG, INDICAÇÃO PÓ PARA SOLUÇÃO ORAL', 'Eurofarma')
    
    # FIX: try_print_anvisa_register, será necessário fazer um expected_conditions customizado