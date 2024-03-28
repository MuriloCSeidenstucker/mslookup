import os
from unidecode import unidecode
import pandas as pd

class OpenDataAnvisa:
    def __init__(self):
        file_path = os.path.join(os.path.dirname(__file__), 'DADOS_ABERTOS_MEDICAMENTOS.xlsx')
        self.df = pd.read_excel(file_path)
        
    def remove_accents_and_spaces(self, input_str):
        return unidecode(input_str.replace(" ", "").lower()) if isinstance(input_str, str) else input_str
        
    def get_register(self, item, description, brand):
        description_normalized = self.remove_accents_and_spaces(description)
        for _, row in self.df.iterrows():
            if row['SITUACAO_REGISTRO'] == 'VÁLIDO':
                product_name = self.remove_accents_and_spaces(row['NOME_PRODUTO'])
                active_principle = self.remove_accents_and_spaces(row['PRINCIPIO_ATIVO']) if isinstance(row['PRINCIPIO_ATIVO'], str) else product_name
                if (product_name in description_normalized or
                    active_principle in description_normalized):
                    
                    cnpj, laboratory = row['EMPRESA_DETENTORA_REGISTRO'].split(' ', 1)
                    if not isinstance(brand, str):
                        if cnpj == brand['CNPJ']:
                            return row['NUMERO_REGISTRO_PRODUTO']
                    else:
                        laboratory = laboratory.strip('- ')
                        laboratory_normalized = self.remove_accents_and_spaces(laboratory)
                        brand_normalized = self.remove_accents_and_spaces(brand)
                        if brand_normalized in laboratory_normalized:
                            return row['NUMERO_REGISTRO_PRODUTO']
        
        return -1
                
            