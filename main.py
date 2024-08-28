from config import load_config
from services.data_processor_service import DataProcessorService
from services.candidate_data_service import CandidateDataService
from services.pdf_processing_service import PDFProcessingService

class ExecutionManager:
    def __init__(self, data_service, candidate_data_service, pdf_processing_service):
        self.data_service = data_service
        self.candidate_data_service = candidate_data_service
        self.pdf_processing_service = pdf_processing_service
        
    def execute(self):
        data = self.data_service.get_data()
        candidate_data = self.candidate_data_service.get_candidate_data(data)
        self.pdf_processing_service.process_candidate_pdfs(candidate_data)
        self.pdf_processing_service.generate_report()


if __name__ == "__main__":
    file_path, item_col, desc_col, brand_col, pdf_manager, anvisa_domain, smerp_search, anvisa_search, report_generator = load_config()

    data_service = DataProcessorService(file_path, item_col, desc_col, brand_col)
    candidate_data_service = CandidateDataService(anvisa_search, smerp_search)
    pdf_processing_service = PDFProcessingService(pdf_manager, anvisa_domain, report_generator)

    manager = ExecutionManager(data_service, candidate_data_service, pdf_processing_service)
    manager.execute()