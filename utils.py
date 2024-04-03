import os
from unidecode import unidecode

class Utils:
    
    @classmethod
    def resize_window(self, driver):
        screen_width = driver.execute_script("return window.screen.availWidth")
        screen_height = driver.execute_script("return window.screen.availHeight")
        new_position = (screen_width // 2, 0)
        new_size = (screen_width // 2, screen_height)
        driver.set_window_position(*new_position)
        driver.set_window_size(*new_size)
        
    @classmethod
    def remove_accents_and_spaces(self, input_str):
        return unidecode(input_str.replace(" ", "").lower()) if isinstance(input_str, str) else input_str
    
    @classmethod
    def calculate_elapsed_time(self, start_time, end_time):
        elapsed_time = end_time - start_time
        hours = int(elapsed_time // 3600)
        minutes = int((elapsed_time % 3600) // 60)
        seconds = elapsed_time % 60
        return f'{hours} hours, {minutes} minutes, and {seconds:.2f} seconds'
    
    @classmethod
    def rename_downloaded_pdf(self, path, new_name):
        files = os.listdir(path)
    
        pdf_file = None
        for file in files:
            if (file.startswith('Consultas - Agência Nacional de Vigilância Sanitária') and
                file.endswith('.pdf')):
                pdf_file = file
                break
        
        if pdf_file:
            old_path = os.path.join(path, pdf_file)
            new_path = os.path.join(path, new_name + '.pdf')
            
            if os.path.exists(new_path):
                base_name, ext = os.path.splitext(new_path)
                i = 1
                while True:
                    new_path = os.path.join(path, f"{base_name} ({i}){ext}")
                    if not os.path.exists(new_path):
                        break
                    i += 1
                    
            os.rename(old_path, new_path)
        else:
            print("Nenhum arquivo PDF com o nome padrão encontrado na pasta de downloads.")
