from unidecode import unidecode

class Utils:
    """
    Classe utilitária com métodos estáticos para realizar várias operações comuns.

    Métodos Estáticos:
        - resize_window(driver): Redimensiona a janela do navegador para ocupar metade da tela.
        - remove_accents_and_spaces(input_str): Remove acentos e espaços de uma string.
        - calculate_elapsed_time(start_time, end_time): Calcula o tempo decorrido entre dois tempos fornecidos.
        - rename_downloaded_pdf(path, new_name): Renomeia um arquivo PDF baixado para um novo nome fornecido.

    Os métodos desta classe podem ser utilizados sem a necessidade de instanciar um objeto Utils.
    """
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
