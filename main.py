from search_and_print import SearchAndPrint
from data_processor import DataProcessor

class Program:

    file_path = r'D:\Documents\Pregoes_Eletr\DM\Em_Andamento\PE_09.1522023_Araxa\Modelo_PE_09.1522023_Araxa.xlsx'
    item_col = 'LOTE'
    desc_col = 'DESCRIÇÃO DO ITEM'
    brand_col = 'MARCA'

    data_processor = DataProcessor(file_path)
    data = data_processor.get_data(item_col, desc_col, brand_col)

    for entry in data:
        print(entry)

    print(f"Número de descrições originais: {data_processor.failed_description_count}")

    # instance = SearchAndPrint()
    # for entry in data:
    #     instance.get_register_as_pdf(entry['description'], entry['brand'])

