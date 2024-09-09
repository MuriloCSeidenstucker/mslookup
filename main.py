from scripts.config import load_config

from scripts.input_manager import InputManager
from scripts.checkpoint_manager import CheckpointManager
from scripts.services.candidate_data_service import CandidateDataService
from scripts.services.pdf_processing_service import PDFProcessingService
from scripts.services.input_processor_service import InputProcessorService

class Main:
    def __init__(self,
                 input_manager: InputManager,
                 checkpoint_manager: CheckpointManager,
                 candidate_data_service: CandidateDataService,
                 pdf_processing_service: PDFProcessingService,
                 input_processor_service: InputProcessorService):
        
        self.input_manager = input_manager
        self.checkpoint_manager = checkpoint_manager
        self.candidate_data_service = candidate_data_service
        self.pdf_processing_service = pdf_processing_service
        self.input_processor_service = input_processor_service
        self.all_stages_completed = False
        
    def execute(self):
        try:
            raw_input = self.input_manager.get_raw_input()
            processed_input = self.input_processor_service.get_processed_input(raw_input)
            candidate_data = self.candidate_data_service.get_candidate_data(processed_input)
            self.pdf_processing_service.process_candidate_pdfs(candidate_data)
            self.pdf_processing_service.generate_report()
            self.all_stages_completed = True
        finally:
            if self.all_stages_completed:
                checkpoint_manager.delete_checkpoints()


if __name__ == "__main__":
    file_path, item_col, desc_col, brand_col, pdf_manager, anvisa_domain, smerp_search, anvisa_search, report_generator = load_config()

    input_manager = InputManager()
    checkpoint_manager = CheckpointManager()
    input_processor_service = InputProcessorService(checkpoint_manager)
    candidate_data_service = CandidateDataService(anvisa_search, smerp_search, checkpoint_manager)
    pdf_processing_service = PDFProcessingService(pdf_manager, anvisa_domain, report_generator)

    main = Main(input_manager, checkpoint_manager, candidate_data_service, pdf_processing_service, input_processor_service)
    main.execute()