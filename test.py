from pdf_manager import PDFManager
from search_in_smerp import SearchInSmerp
from report_generator import ReportGenerator
from access_anvisa_domain import AnvisaDomain
from search_in_open_data_anvisa import OpenDataAnvisa

from services.data_processor_service import DataProcessorService
from services.candidate_data_service import CandidateDataService
from services.pdf_processing_service import PDFProcessingService

class Test:
    def __init__(self, file_path, item_col, desc_col, brand_col, pdf_manager, anvisa_domain, smerp_search, anvisa_search, report_generator):
            self.data_service = DataProcessorService(file_path, item_col, desc_col, brand_col)
            self.candidate_data_service = CandidateDataService(anvisa_search, smerp_search)
            self.pdf_processing_service = PDFProcessingService(pdf_manager, anvisa_domain, report_generator)
        
    def run(self):
        data = self.data_service.get_data()
        candidate_data = self.candidate_data_service.get_candidate_data(data)
        self.pdf_processing_service.process_candidate_pdfs(candidate_data)
        self.pdf_processing_service.generate_report()

if __name__ == "__main__":
    # file_path = r"data_for_testing\Controle_Operacao_PE_090092024_Araxa.xlsm"
    # file_path = r"data_for_testing\Controle_Operacao_PE_042024_Frutal.xlsm"
    # file_path = r"data_for_testing\Controle_Operacao_PE_112024_Campina-Verde.xlsm"
    file_path = r"D:\Documents\Licitacoes\DM\Preg Eletr\Cadastrar\PE_900172024_Catalao\Controle_Operacao_PE_900172024_Catalao.xlsm"
    item_col = 'ITEM'
    desc_col = 'DESCRIÇÃO'
    brand_col = 'MARCA'
    pdf_manager = PDFManager()
    anvisa_domain = AnvisaDomain(pdf_manager)
    smerp_search = SearchInSmerp()
    anvisa_search = OpenDataAnvisa()
    report_generator = ReportGenerator()
    
    main = Test(file_path, item_col, desc_col, brand_col, pdf_manager, anvisa_domain, smerp_search, anvisa_search, report_generator)
    main.run()