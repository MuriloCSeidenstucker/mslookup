import os

import pandas as pd

from utils import Utils
from datetime import datetime
from typing import Union, List, Dict

class OpenDataAnvisa:
    '''
    Classe para gerenciar e consultar dados de registros de medicamentos fornecidos pela Anvisa.

    Esta classe carrega dados de um arquivo Excel contendo registros de medicamentos, filtra os registros válidos
    e os organiza em um formato estruturado. Ela fornece um método para buscar registros específicos de medicamentos
    com base em uma descrição e marca fornecidas.
    
    Funcionamento:
    --------------
    1. Inicialização: Ao instanciar a classe, os dados do arquivo 'DADOS_ABERTOS_MEDICAMENTOS.xlsx' são carregados em um DataFrame.
    Apenas os registros com situação 'VÁLIDO' são mantidos.
    2. Mapeamento de Dados: O método `create_data_map` cria um dicionário onde cada chave é o nome de um laboratório e o valor é outro dicionário
    contendo os registros de medicamentos desse laboratório.
    3. Busca de Registros: O método `get_register` permite buscar um registro de medicamento específico com base em uma descrição e uma marca.
    Ele normaliza a descrição, verifica as substâncias ativas e retorna o número do registro e a data de vencimento do produto, se encontrado.
    '''
    def __init__(self):
        file_path = os.path.join(os.path.dirname(__file__), 'DADOS_ABERTOS_MEDICAMENTOS.xlsx')
        self.df = pd.read_excel(file_path)
        self.df = self.df[self.df['SITUACAO_REGISTRO'] == 'VÁLIDO'].copy()
        self.laboratory_registers = self.create_data_map()
        
    def create_data_map(self):
        '''
        Cria um mapa de dados de registros de medicamentos organizados por laboratório.

        Este método itera sobre o DataFrame carregado, extraindo e formatando informações relevantes
        de cada registro de medicamento. Ele organiza esses registros em um dicionário onde cada chave 
        é o nome de um laboratório e cada valor é outro dicionário contendo os registros de medicamentos
        desse laboratório.

        Returns:
            Dict[str, Dict[str, Any]]: Um dicionário aninhado onde cada chave é o nome de um laboratório e cada valor é um dicionário
            que mapeia os números de registro dos medicamentos para seus detalhes, incluindo nome do produto,
            data de vencimento, CNPJ e substâncias ativas.
        '''
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
                print(f'Registro {register} já existe no laboratório {laboratory}')
                
        return laboratories
        
    def validate_arguments(self, description: str, laboratory: Union[str, Dict]) -> None:
        if not isinstance(description, str) or not description.strip():
            raise ValueError('description deve ser uma string não vazia.')
        
        if not isinstance(laboratory, (str, dict)):
            raise ValueError('laboratory deve ser uma string ou um dicionário.')
        
        if isinstance(laboratory, dict):
            if 'Name' not in laboratory or not isinstance(laboratory['Name'], str) or not laboratory['Name'].strip():
                raise ValueError('O dicionário laboratory deve conter a chave "Name" com um valor string não vazio.')
            if 'Linked' in laboratory and not isinstance(laboratory['Linked'], list):
                raise ValueError('A chave "Linked" em laboratory, se presente, deve ser uma lista.')
    
    def get_laboratory_candidates(self, laboratory: Union[str, Dict]) -> List[str]:
        if isinstance(laboratory, str):
            return [laboratory]
        
        if isinstance(laboratory, dict):
            candidates = [laboratory.get('Name', '')]
            linked = laboratory.get('Linked', [])
            if isinstance(linked, list):
                candidates.extend(linked)
            return [candidate for candidate in candidates if candidate]
        
        raise ValueError("laboratory deve ser uma string ou um dicionário.")
    
    def get_register(self, description: str, laboratory: Union[str, Dict]) -> List[Dict[str, Union[str, int]]]:
        '''
        Busca um registro de medicamento com base em uma descrição e marca fornecidas.

        Este método normaliza a descrição, verifica as substâncias ativas e busca correspondências nos registros
        de medicamentos organizados por laboratório. Se encontrar uma correspondência, retorna o número do registro
        e a data de vencimento do produto.

        Args:
            description (str): A descrição do medicamento.
            laboratory (Union[str, dict]): O nome da marca ou um dicionário contendo detalhes da marca. Se for um dicionário, espera-se que
            contenha a chave 'Name' e, opcionalmente, 'Linked' com nomes relacionados.

        Returns:
            Tuple[str, str]: Uma tupla contendo o número do registro e a data de vencimento formatada no formato 'dd/mm/aaaa' 
            se uma correspondência for encontrada, ou (-1, -1) se não houver correspondência.
        '''
        self.validate_arguments(description, laboratory)
        description_normalized = Utils.remove_accents_and_spaces(description)
        laboratory_candidates = self.get_laboratory_candidates(laboratory)
        
        reg_candidates = []
        for laboratory_candidate in laboratory_candidates:
            #FIX: laboratory_candidate pode não ser uma chave.
            if laboratory_candidate in self.laboratory_registers:
                for register in self.laboratory_registers[laboratory_candidate]:
                    register_data = self.laboratory_registers[laboratory_candidate][register]
                    selected_subs = description_normalized.split(';')
                    if len(register_data['substances']) != len(selected_subs):
                        continue
                    for substance in register_data['substances']:
                        sub_normalized = Utils.remove_accents_and_spaces(substance)
                        if sub_normalized in selected_subs:
                            date_formatted = -1
                            if register_data['expiration_date'] != 'nan':
                                date = datetime.strptime(register_data['expiration_date'], '%Y-%m-%d %H:%M:%S')
                                if isinstance(date, str) or isinstance(date, datetime):
                                    date_formatted = date.strftime('%d/%m/%Y')
                            reg_candidates.append(
                                {
                                    'register': register,
                                    'process_number': -1,
                                    'expiration_date': date_formatted
                                }
                            )
                    
        # As descrições dos medicamentos podem trazer substâncias fora da ordem esperada, por exemplo: Sódio Cloreto.
        if not reg_candidates:
            words = description_normalized.split(';')
            for laboratory_candidate in laboratory_candidates:
                if laboratory_candidate in self.laboratory_registers:
                    for register in self.laboratory_registers[laboratory_candidate]:
                        register_data = self.laboratory_registers[laboratory_candidate][register]
                        for substance in register_data['substances']:
                            sub_normalized = Utils.remove_accents_and_spaces(substance)
                            if all(word in sub_normalized for word in words):
                                date_formatted = -1
                                if register_data['expiration_date'] != 'nan':
                                    date = datetime.strptime(register_data['expiration_date'], '%Y-%m-%d %H:%M:%S')
                                    if isinstance(date, str) or isinstance(date, datetime):
                                        date_formatted = date.strftime('%d/%m/%Y')
                                reg_candidates.append(
                                    {
                                        'register': register,
                                        'process_number': -1,
                                        'expiration_date': date_formatted
                                    }
                                )
                            
        return reg_candidates