import os
import pandas as pd

from utils import Utils
from pdf_manager import PDFManager
from data_processor import DataProcessor
from search_in_smerp import SearchInSmerp
from access_anvisa_domain import AnvisaDomain
from search_in_open_data_anvisa import OpenDataAnvisa

class Test:

    # FILE_PATH = r"data_for_testing\Controle_Operacao_PE_112024_Campina-Verde.xlsm"
    # FILE_PATH = r"D:\Projects\LearningSeleniumAndPython\data_for_testing\Itens_Errados.xlsx"
    # FILE_PATH = r"data_for_testing\Controle_Operacao_PE_042024_Frutal.xlsm"
    FILE_PATH = r"data_for_testing\Controle_Operacao_PE_090092024_Araxa.xlsm"
    # FILE_PATH = r"data_for_testing\Controle_Operacao_000000_Cidade.xlsm"
    ITEM_COL = 'ITEM'
    DESC_COL = 'DESCRIÇÃO'
    BRAND_COL = 'MARCA'
    
    def __init__(self):
        print("Executando __init__")
        self.data_processor = DataProcessor(self.FILE_PATH)
        self.data = self.data_processor.get_data(self.ITEM_COL, self.DESC_COL, self.BRAND_COL)
        self.pdfManager = PDFManager()
        self.anvisaDomain = AnvisaDomain()
        self.smerp_search = SearchInSmerp()
        self.anvisa_search = OpenDataAnvisa()
        self.report_data = []
        self.d_path = os.path.join(os.path.expanduser('~'), 'Downloads')

    def run(self):
        reg_candidates = self.get_candidate_data()
                
        has_pdf = False
        if reg_candidates:
            for reg in reg_candidates:
                has_pdf_in_db = self.pdfManager.get_pdf_in_db(reg['register'])
                
                if not has_pdf_in_db:
                    self.anvisaDomain.get_register_as_pdf(
                        reg['register'],
                        entry['concentration'],
                        reg['process_number']
                    )
                    self.pdfManager.copy_and_rename_file(
                        self.d_path,
                        reg['register'],
                        reg['expiration_date']
                    )
                    
                has_pdf = Utils.rename_downloaded_pdf(self.d_path, f'Item {entry['item']}')
            
        self.report_data.append({'Item': entry['item'],
                            'Descrição': entry['description'],
                            'Marca': entry['brand'] if isinstance(entry['brand'], str) else entry['brand']['Name'],
                            'Registro': registration_data['registration'] if registration_data['registration'] != -1 else 'Não encontrado',
                            'PDF': 'OK' if has_pdf else 'Pendente',
                            })
            
        self.generate_report()
        
    def get_candidate_data(self):
        candidate_data = []
        for i, entry in enumerate(self.data):
            candidate_data.append(
                {
                    'item': entry['item'],
                    'concentration': entry['concentration'],
                    'reg_candidates': self.get_registration_data(entry['description'], entry['brand'])
                }
            )
            self.report_data.append(
                {
                    'Item': entry['item'],
                    'Descrição': entry['description'],
                    'Marca': entry['brand'] if isinstance(entry['brand'], str) else entry['brand']['Name'],
                }
            )
        return candidate_data
            
    
    def generate_report(self):
        report_df = pd.DataFrame(self.report_data)
        report_df.to_excel('relatorio_registros.xlsx', index=False)

    def get_registration_data(self, a_description, a_laboratory):
        reg_candidates =[]
        
        reg_candidates = self.anvisa_search.get_register(a_description, a_laboratory)
        if not reg_candidates:
            # Estou considerando apenas o primeiro caso que estiver correto.
            reg_candidates = self.smerp_search.get_data_from_smerp(a_description, a_laboratory)
        
        return reg_candidates
    
if __name__ == "__main__":
    test = Test()
    test.run()