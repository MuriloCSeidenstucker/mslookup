from mslookup.app.checkpoint_manager import CheckpointManager
from mslookup.app.config import load_config
from mslookup.app.input_manager import InputManager
from mslookup.app.report_generator import ReportGenerator
from mslookup.app.services.input_processor_service import InputProcessorService
from mslookup.app.services.product_registration_service import \
    ProductRegistrationService
from mslookup.app.services.registration_pdf_service import RegistrationPDFService


class Core:
    def __init__(self):

        pdf_manager, anvisa_domain = load_config()

        self.input_manager = InputManager()
        self.report_generator = ReportGenerator()
        self.checkpoint_manager = CheckpointManager()
        self.input_processor_service = InputProcessorService(self.checkpoint_manager)
        self.product_registration_service = ProductRegistrationService(
            self.checkpoint_manager
        )
        self.registration_pdf_service = RegistrationPDFService(
            pdf_manager, anvisa_domain
        )
        self.all_stages_completed = False

    def execute(self, raw_input):
        try:
            # raw_input = self.input_manager.get_raw_input()
            processed_input = self.input_processor_service.get_processed_input(
                raw_input
            )
            product_registrations = (
                self.product_registration_service.get_product_registrations(
                    processed_input
                )
            )
            final_result = (
                self.registration_pdf_service.generate_registration_pdfs(
                    product_registrations
                )
            )
            self.report_generator.generate_report(final_result)
            self.all_stages_completed = True
        finally:
            if self.all_stages_completed:
                self.checkpoint_manager.delete_checkpoints()
