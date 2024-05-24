import os
import pandas as pd

from utils import Utils
from datetime import datetime

class OpenDataAnvisa:
    def __init__(self):
        file_path = os.path.join(os.path.dirname(__file__), 'DADOS_ABERTOS_MEDICAMENTOS.xlsx')
        self.df = pd.read_excel(file_path)
        self.df = self.df[self.df['SITUACAO_REGISTRO'] == 'VÁLIDO'].copy()
        self.laboratory_registers = self.create_data_map()
        
    def create_data_map(self):
        laboratories = {}

        for index, row in self.df.iterrows():
            lab_cnpj, laboratory = str(row['EMPRESA_DETENTORA_REGISTRO']).split(' ', 1)
            laboratory = laboratory.strip('- ')
            register = str(row['NUMERO_REGISTRO_PRODUTO'])
            product_name = str(row['NOME_PRODUTO'])
            expiration_date = str(row['DATA_VENCIMENTO_REGISTRO'])
            substances = [substance.strip() for substance in str(row['PRINCIPIO_ATIVO']).split('+')] if row['PRINCIPIO_ATIVO'] is not None else []
            
            if laboratory not in laboratories:
                laboratories[laboratory] = {}
            
            if register not in laboratories[laboratory]:
                laboratories[laboratory][register] = {
                    'product_name': product_name,
                    'expiration_date': expiration_date,
                    'cnpj': lab_cnpj,
                    'substances': substances
                }
            else:
                print(f"Registro {register} já existe no laboratório {laboratory}")
                
        return laboratories
        
    def get_register(self, item, description, brand):
        description_normalized = Utils.remove_accents_and_spaces(description)
        
        brand_candidates = [brand["Name"]] + (brand.get("Linked", [])
                                              if isinstance(brand, dict)
                                              else []) if not isinstance(brand, str) else [brand]
        
        for brand_candidate in brand_candidates:
            #FIX: brand_candidate pode não ser uma chave.
            if brand_candidate in self.laboratory_registers:
                for register in self.laboratory_registers[brand_candidate]:
                    register_data = self.laboratory_registers[brand_candidate][register]
                    selected_subs = description_normalized.split(';')
                    if len(register_data['substances']) != len(selected_subs):
                        continue
                    for substance in register_data['substances']:
                        sub_normalized = Utils.remove_accents_and_spaces(substance)
                        if sub_normalized in selected_subs:
                            selected_subs.remove(sub_normalized)
                        if not selected_subs:
                            date = datetime.strptime(register_data['expiration_date'], '%Y-%m-%d %H:%M:%S')
                            if isinstance(date, str) or isinstance(date, datetime):
                                date_formatted = date.strftime("%d/%m/%Y")
                            else:
                                print(f'{date} is NAN')
                                date = -1
                            return register, date_formatted
                        
        words = description_normalized.split(';')
        for brand_candidate in brand_candidates:
            if brand_candidate in self.laboratory_registers:
                for register in self.laboratory_registers[brand_candidate]:
                    register_data = self.laboratory_registers[brand_candidate][register]
                    for substance in register_data['substances']:
                        sub_normalized = Utils.remove_accents_and_spaces(substance)
                        if all(word in sub_normalized for word in words):
                            date = datetime.strptime(register_data['expiration_date'], '%Y-%m-%d %H:%M:%S')
                            if isinstance(date, str) or isinstance(date, datetime):
                                date_formatted = date.strftime("%d/%m/%Y")
                            else:
                                print(f'{date} is NAN')
                                date = -1
                            return register, date_formatted
        
        # for brand_candidate in brand_candidates:
        #     for _, row in self.df.iterrows():
        #         if row['SITUACAO_REGISTRO'] == 'VÁLIDO':
        #             product_name = Utils.remove_accents_and_spaces(row['NOME_PRODUTO'])
        #             active_principle = Utils.remove_accents_and_spaces(row['PRINCIPIO_ATIVO']) if isinstance(row['PRINCIPIO_ATIVO'], str) else product_name
        #             if (product_name in description_normalized or
        #                 active_principle in description_normalized):
                        
        #                 cnpj, laboratory = row['EMPRESA_DETENTORA_REGISTRO'].split(' ', 1)
        #                 laboratory = laboratory.strip('- ')
        #                 laboratory_normalized = Utils.remove_accents_and_spaces(laboratory)
        #                 brand_normalized = Utils.remove_accents_and_spaces(brand_candidate)
        #                 if (brand_normalized == laboratory_normalized or
        #                     brand_normalized in laboratory_normalized):
        #                     date = row['DATA_VENCIMENTO_REGISTRO']
        #                     if isinstance(date, str) or isinstance(date, datetime):
        #                         date = date.strftime("%d/%m/%Y")
        #                     else:
        #                         print(f'{date} is NAN')
        #                         date = -1
        #                     return row['NUMERO_REGISTRO_PRODUTO'], date
        return -1, -1
                
            