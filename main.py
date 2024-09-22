from src.config import load_config

from src.input_manager import InputManager
from src.report_generator import ReportGenerator
from src.checkpoint_manager import CheckpointManager
from src.services.input_processor_service import InputProcessorService
from src.services.registration_pdf_service import RegistrationPDFService
from src.services.product_registration_service import ProductRegistrationService

class Main:
    def __init__(self,
                 input_manager: InputManager,
                 report_generator: ReportGenerator,
                 checkpoint_manager: CheckpointManager,
                 input_processor_service: InputProcessorService,
                 registration_pdf_service: RegistrationPDFService,
                 product_registration_service: ProductRegistrationService):
        
        self.input_manager = input_manager
        self.report_generator = report_generator
        self.checkpoint_manager = checkpoint_manager
        self.input_processor_service = input_processor_service
        self.registration_pdf_service = registration_pdf_service
        self.product_registration_service = product_registration_service
        self.all_stages_completed = False
        
    def execute(self):
        try:
            raw_input = self.input_manager.get_raw_input()
            processed_input = self.input_processor_service.get_processed_input(raw_input)
            product_registrations = self.product_registration_service.get_product_registrations(processed_input)
            final_result = self.registration_pdf_service.generate_registration_pdfs(product_registrations)
            self.report_generator.generate_report(final_result)
            self.all_stages_completed = True
        finally:
            if self.all_stages_completed:
                checkpoint_manager.delete_checkpoints()


if __name__ == "__main__":
    pdf_manager, anvisa_domain = load_config()

    input_manager = InputManager()
    report_generator = ReportGenerator()
    checkpoint_manager = CheckpointManager()
    input_processor_service = InputProcessorService(checkpoint_manager)
    product_registration_service = ProductRegistrationService(checkpoint_manager)
    registration_pdf_service = RegistrationPDFService(pdf_manager, anvisa_domain)

    main = Main(
        input_manager = input_manager,
        report_generator = report_generator,
        checkpoint_manager = checkpoint_manager,
        input_processor_service = input_processor_service,
        registration_pdf_service = registration_pdf_service,
        product_registration_service = product_registration_service)
    
    main.execute()