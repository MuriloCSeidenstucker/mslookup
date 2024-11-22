

import pandas as pd
from mslookup.app.checkpoint_manager import CheckpointManager
from mslookup.app.config import load_config
from mslookup.app.exceptions import MissingColumnsError
from mslookup.app.input_manager import InputManager
from mslookup.app.logger_config import get_logger
from mslookup.app.report_generator import ReportGenerator
from mslookup.app.services.input_processor_service import InputProcessorService
from mslookup.app.services.product_registration_service import \
    ProductRegistrationService
from mslookup.app.services.registration_pdf_service import RegistrationPDFService
from mslookup.app.utils import Utils


class Core:
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        
        self.logger.info('Instantiated.')
        
        pdf_manager, anvisa_domain = load_config()
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
        
        # Método para detectar colunas automaticamente
    def detect_columns(self, file_path):
        try:
            # Carrega o arquivo
            df = pd.read_excel(file_path) if file_path.endswith(('.xls', '.xlsx', '.xlsm')) else pd.read_csv(file_path)

            # Listas de opções de nomes para cada coluna
            item_options = ['item', 'itens', 'lote']
            desc_options = ['descricao', 'especificacao']
            brand_options = ['marca', 'laboratorio']

            # Função para encontrar a coluna exata com base nas opções
            def find_column(options):
                for col in df.columns:
                    filtered_col = Utils.remove_accents_and_spaces(str(col))
                    if filtered_col in options:
                        return col
                return None

            # Detecta as colunas usando as listas de opções
            item_col = find_column(item_options)
            desc_col = find_column(desc_options)
            brand_col = find_column(brand_options)

            return {
                'item_col': item_col,
                'desc_col': desc_col,
                'brand_col': brand_col
            }
        except Exception as e:
            self.logger.error(f'Core: Error detecting columns - {e}')
            return None

    def execute(self, raw_input, progress_callback):
        self.logger.info('Starting execution.')
        try:
            processed_input = self.input_processor_service.get_processed_input(
                raw_input,
                progress_callback=lambda progress: progress_callback(progress)
            )
            self.logger.info('Processed data input.')
            
            product_registrations = (
                self.product_registration_service.get_product_registrations(
                    processed_input,
                    progress_callback=lambda progress: progress_callback(progress)
                )
            )
            self.logger.info('Registrations of collected products.')
            
            final_result = (
                self.registration_pdf_service.generate_registration_pdfs(
                    product_registrations,
                    progress_callback=lambda progress: progress_callback(progress)
                )
            )
            self.logger.info('PDF registrations generated.')
            
            self.report_generator.generate_report(final_result)
            progress_callback(100)  # Atualiza para 100%
            self.logger.info('Report generated successfully.')
            
            self.all_stages_completed = True
        except MissingColumnsError:
            raise
        except Exception as e:
            self.logger.critical(f'Unexpected error {e=}, {type(e)=}')
            raise
        finally:
            if self.all_stages_completed:
                self.checkpoint_manager.delete_checkpoints()
            self.logger.info('Execution completed.')
                
# if __name__ == '__main__':
#     core = Core()
#     inp = InputManager()
#     raw_input = inp.get_raw_input()
#     core.execute(raw_input)
