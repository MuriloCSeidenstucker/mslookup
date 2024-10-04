from mslookup.config import load_config
from mslookup.services.input_processor_service import InputProcessorService
from mslookup.services.product_registration_service import \
    ProductRegistrationService
from mslookup.services.registration_pdf_service import RegistrationPDFService


class Test:
    def __init__(
        self, data_service, candidate_data_service, pdf_processing_service
    ):
        self.data_service = data_service
        self.candidate_data_service = candidate_data_service
        self.pdf_processing_service = pdf_processing_service

    def execute(self):
        data = self.data_service.get_data()
        candidate_data = self.candidate_data_service.get_candidate_data(data)
        self.pdf_processing_service.process_candidate_pdfs(candidate_data)
        self.pdf_processing_service.generate_report()


if __name__ == '__main__':
    (
        file_path,
        item_col,
        desc_col,
        brand_col,
        pdf_manager,
        anvisa_domain,
        smerp_search,
        anvisa_search,
        report_generator,
    ) = load_config()

    data_service = InputProcessorService(
        file_path, item_col, desc_col, brand_col
    )
    candidate_data_service = ProductRegistrationService(
        anvisa_search, smerp_search
    )
    pdf_processing_service = RegistrationPDFService(
        pdf_manager, anvisa_domain, report_generator
    )

    manager = Test(
        data_service, candidate_data_service, pdf_processing_service
    )
    manager.execute()
