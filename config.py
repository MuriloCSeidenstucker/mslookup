from pdf_manager import PDFManager
from search_in_smerp import SearchInSmerp
from report_generator import ReportGenerator
from access_anvisa_domain import AnvisaDomain
from search_in_open_data_anvisa import OpenDataAnvisa

def load_config():
    file_path = r"data_for_testing\Controle_Operacao_PE_090092024_Araxa.xlsm"
    item_col = 'ITEM'
    desc_col = 'DESCRIÇÃO'
    brand_col = 'MARCA'
    
    pdf_manager = PDFManager()
    anvisa_domain = AnvisaDomain(pdf_manager)
    smerp_search = SearchInSmerp()
    anvisa_search = OpenDataAnvisa()
    report_generator = ReportGenerator()
    
    return (file_path,
            item_col,
            desc_col,
            brand_col,
            pdf_manager,
            anvisa_domain,
            smerp_search,
            anvisa_search,
            report_generator)