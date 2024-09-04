from config import load_config
from input import Input
from services.data_processor_service import DataProcessorService
from services.candidate_data_service import CandidateDataService
from services.pdf_processing_service import PDFProcessingService
from checkpoint_manager import CheckpointManager

class Main:
    def __init__(self, data_service, candidate_data_service, pdf_processing_service, checkpoint_manager):
        self.data_service = data_service
        self.candidate_data_service = candidate_data_service
        self.pdf_processing_service = pdf_processing_service
        self.checkpoint_manager = checkpoint_manager
        self.all_stages_completed = False
        
    def execute(self):
        try:
            data = self.data_service.get_data()
            candidate_data = self.candidate_data_service.get_candidate_data(data)
            self.pdf_processing_service.process_candidate_pdfs(candidate_data)
            self.pdf_processing_service.generate_report()
            self.all_stages_completed = True
        finally:
            if self.all_stages_completed:
                checkpoint_manager.delete_checkpoints()


if __name__ == "__main__":
    file_path, item_col, desc_col, brand_col, pdf_manager, anvisa_domain, smerp_search, anvisa_search, report_generator = load_config()

    input = Input()
    entry = input.start()
    checkpoint_manager = CheckpointManager()
    data_service = DataProcessorService(entry, checkpoint_manager)
    candidate_data_service = CandidateDataService(anvisa_search, smerp_search, checkpoint_manager)
    pdf_processing_service = PDFProcessingService(pdf_manager, anvisa_domain, report_generator)
    

    main = Main(data_service, candidate_data_service, pdf_processing_service, checkpoint_manager)
    main.execute()