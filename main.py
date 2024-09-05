from config import load_config
from input import Input
from services.input_processor_service import InputProcessorService
from services.candidate_data_service import CandidateDataService
from services.pdf_processing_service import PDFProcessingService
from checkpoint_manager import CheckpointManager

class Main:
    def __init__(self,
                 input_processor_service: InputProcessorService,
                 candidate_data_service: CandidateDataService,
                 pdf_processing_service: PDFProcessingService,
                 input_manager: Input,
                 checkpoint_manager: CheckpointManager):
        
        self.input_processor_service = input_processor_service
        self.candidate_data_service = candidate_data_service
        self.pdf_processing_service = pdf_processing_service
        self.input_manager = input_manager
        self.checkpoint_manager = checkpoint_manager
        self.all_stages_completed = False
        
    def execute(self):
        try:
            raw_input = self.input_manager.get_input()
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

    input_manager = Input()
    checkpoint_manager = CheckpointManager()
    input_processor_service = InputProcessorService(checkpoint_manager)
    candidate_data_service = CandidateDataService(anvisa_search, smerp_search, checkpoint_manager)
    pdf_processing_service = PDFProcessingService(pdf_manager, anvisa_domain, report_generator)

    main = Main(input_processor_service, candidate_data_service, pdf_processing_service, input_manager, checkpoint_manager)
    main.execute()