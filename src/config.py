from src.pdf_manager import PDFManager
from src.report_generator import ReportGenerator
from src.access_anvisa_domain import AnvisaDomain

def load_config():
    pdf_manager = PDFManager()
    anvisa_domain = AnvisaDomain(pdf_manager)
    report_generator = ReportGenerator()
    
    return (pdf_manager,
            anvisa_domain,
            report_generator)