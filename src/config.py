from src.pdf_manager import PDFManager
from src.access_anvisa_domain import AnvisaDomain

def load_config():
    pdf_manager = PDFManager()
    anvisa_domain = AnvisaDomain(pdf_manager)
    
    return (pdf_manager,
            anvisa_domain)