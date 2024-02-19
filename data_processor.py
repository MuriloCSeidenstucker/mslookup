from unidecode import unidecode
import os
import pandas as pd

class DataProcessor:
    def __init__(self, file_path):
        self.df = pd.read_excel(file_path)
        reference_path = os.path.join(os.path.dirname(__file__), 'data_reference.xlsx')
        self.reference_df = pd.read_excel(reference_path)
        self.failed_description_count = 0

    def get_data(self, item_col, desc_col, brand_col):
        data = []
        for index, row in self.df.iterrows():
            if pd.notna(row[brand_col]):
                description = self.get_filtered_description(row[desc_col])
                data.append({'item': row[item_col], 'description': description, 'brand': row[brand_col]})
        return data
    
    def remove_accents_and_spaces(self, input_str):
        return unidecode(input_str.replace(" ", "").lower()) if isinstance(input_str, str) else input_str
    
    def get_filtered_description(self, description):
        # Remover acentuação, espaços em branco e caracteres especiais para comparação
        description_normalized = self.remove_accents_and_spaces(description)

        # Iterar sobre as linhas da planilha de referência
        for _, ref_row in self.reference_df.iterrows():
            ref_farmaco_normalized = self.remove_accents_and_spaces(ref_row['FARMACO'])
            ref_medicamento_normalized = self.remove_accents_and_spaces(str(ref_row['MEDICAMENTO']))
            ref_concentracao_normalized = self.remove_accents_and_spaces(str(ref_row['CONCENTRAÇÃO']))

            # Verificar se os valores da coluna 'FARMACO' e 'CONCENTRACAO' estão presentes na descrição
            if (ref_farmaco_normalized in description_normalized or
                ref_medicamento_normalized in description_normalized):

                correct_farmaco = ''
                correct_medicamento = ''
                correct_concentracao = ''

                if (ref_concentracao_normalized in description_normalized):
                    correct_concentracao = ref_row['CONCENTRAÇÃO']
                    
                # Se houver correspondência, use os valores corretos de 'FARMACO' e 'CONCENTRACAO'
                correct_farmaco = ref_row['FARMACO']
                correct_medicamento = ref_row['MEDICAMENTO']

                # Construa a descrição correta
                correct_description = f"{correct_farmaco} {correct_medicamento} {correct_concentracao}"
                return correct_description

        # Se não encontrou correspondência, retorne a descrição original
        self.failed_description_count += 1
        return f'Original: {description}'
