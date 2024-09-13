from src.pdf_manager import PDFManager
from src.search_in_smerp import SearchInSmerp
from src.report_generator import ReportGenerator
from src.access_anvisa_domain import AnvisaDomain
from src.search_in_open_data_anvisa import OpenDataAnvisa

def load_config():
    pdf_manager = PDFManager()
    anvisa_domain = AnvisaDomain(pdf_manager)
    smerp_search = SearchInSmerp()
    anvisa_search = OpenDataAnvisa()
    report_generator = ReportGenerator()
    
    return (pdf_manager,
            anvisa_domain,
            smerp_search,
            anvisa_search,
            report_generator)