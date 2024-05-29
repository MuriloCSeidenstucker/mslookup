import os
import re
import shutil

from datetime import datetime

class PDFManager:
    """
    Classe responsável pela gestão de arquivos PDF relacionados a registros.

    Esta classe oferece métodos para buscar e manipular arquivos PDF com base em registros
    e datas de expiração específicas.
    """
    def get_pdf_in_db(self, target_reg):
        """
        Busca um arquivo PDF correspondente ao número de registro fornecido no diretório 'registers_pdf'.

        Args:
            target_reg (int): O número de registro a ser buscado.

        Returns:
            bool: True se o arquivo PDF correspondente ao registro for encontrado e copiado com sucesso,
            False se o registro não for encontrado ou se o arquivo estiver vencido.
        """
        pattern = r'(\d{9})_(\d{2}-\d{2}-\d{4})'

        path = 'registers_pdf'

        for file in os.listdir(path):
            file_path = os.path.join(path, file)
            
            if os.path.isfile(file_path):
                match = re.match(pattern, file)
                
                if match:
                    expiration_date = match.group(2)
                    register = match.group(1)
                        
                    if int(target_reg) == int(register):
                        dt = datetime.strptime(expiration_date, '%d-%m-%Y')
                        if dt < datetime.now():
                            print(f'{file} está vencido')
                            return False
                        
                        target_path = os.path.join(os.path.expanduser('~'), 'Downloads')
                        new_file_name = 'Consultas - Agência Nacional de Vigilância Sanitária.pdf'
                        destination_path = os.path.join(target_path, new_file_name)
                        shutil.copy2(file_path, destination_path)
                        print(f'{target_reg} encontrado em {file}')
                        return True
                    
        print(f'{target_reg} não encontrado')
        return False
    
    def copy_and_rename_file(self, origin_path, register, expiration_date):
        """
        Copia e renomeia um arquivo PDF do diretório de origem para o diretório 'registers_pdf'
        com base no número de registro e na data de expiração fornecidos.

        Args:
            origin_path (str): O caminho para o diretório de origem onde o arquivo PDF está localizado.
            register (str): O número de registro associado ao arquivo PDF.
            expiration_date (str): A data de expiração associada ao arquivo PDF no formato 'dd/mm/yyyy',
                ou '-1' se não houver data de expiração.
        """ 
        exp_date_formated = expiration_date.replace('/', '-') if expiration_date != -1 else 'sem-data'
        
        target_path = 'registers_pdf'

        searched_file_name = "Consultas - Agência Nacional de Vigilância Sanitária.pdf"

        if os.path.exists(origin_path):
            for file in os.listdir(origin_path):
                file_path = os.path.join(origin_path, file)
                
                if os.path.isfile(file_path) and file == searched_file_name:
                    new_file_name = f'{register}_{exp_date_formated}.pdf'
                    destination_path = os.path.join(target_path, new_file_name)
                    shutil.copy2(file_path, destination_path)
                    print("Arquivo copiado e renomeado com sucesso.")
                    break  # Parar o loop após encontrar o arquivo desejado
            else:
                print("Nenhum arquivo com o nome procurado foi encontrado.")
        else:
            print("O diretório de origem especificado não existe.")

