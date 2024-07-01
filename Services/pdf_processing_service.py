class PDFProcessingService:
    def __init__(self, pdf_manager, anvisa_domain, report_generator):
        self.pdf_manager = pdf_manager
        self.anvisa_domain = anvisa_domain
        self.report_generator = report_generator
    
    def process_candidate_pdfs(self, candidate_data):
        for candidate in candidate_data:
            if candidate['reg_candidates']:
                first_reg = candidate['reg_candidates'][0]
                has_pdf_in_db = self.pdf_manager.get_pdf_in_db(first_reg['register'])
                if not has_pdf_in_db:
                    self.anvisa_domain.get_register_as_pdf(
                        first_reg['register'],
                        candidate['concentration'],
                        first_reg['process_number']
                    )
                    self.pdf_manager.copy_and_rename_file(
                        first_reg['register'],
                        first_reg['expiration_date']
                    )
                
                has_pdf = self.pdf_manager.rename_downloaded_pdf(f'Item {candidate["item"]}')
                self.report_generator.add_entry({
                    'Item': candidate['item'],
                    'Descrição': candidate['description'],
                    'Concentração_Obtida': candidate['concentration'],
                    'Laboratório': candidate['laboratory'],
                    'Registro': first_reg['register'] if first_reg['register'] != -1 else 'Não encontrado',
                    'PDF': 'OK' if has_pdf else 'Pendente',
                })
                
    def generate_report(self):
        self.report_generator.generate_report()