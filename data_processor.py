import cProfile
import os
import json
import pandas as pd

from utils import Utils

class DataProcessor:
    def __init__(self, file_path):
        """
        Inicializa o DataProcessor com o caminho para a planilha de medicamentos.

        Esta classe acessa uma planilha que contém informações sobre medicamentos e coleta
        dados importantes para a futura obtenção dos registros.

        Args:
            file_path (str): O caminho para a planilha que será utilizada para a coleta dos dados.
        """
        self.df = pd.read_excel(file_path)
        
        with open('laboratories.json', 'r', encoding='utf-8') as file:
            self.labs_json = json.load(file)
        self.abbreviation_map = self.create_abbreviation_map()
        
        reference_path = os.path.join(os.path.dirname(__file__), 'TA_PRECO_MEDICAMENTO_GOV.xlsx')
        selected_columns = ['SUBSTÂNCIA', 'CNPJ', 'LABORATÓRIO', 'EAN 1', 'PRODUTO', 'APRESENTAÇÃO']
        self.reference_df = pd.read_excel(reference_path, skiprows=52, usecols=selected_columns)
        self.substances_set, self.shortest_substance = self.process_substances()
        
        self.PREPOSITIONS = [
            'a', 'ante', 'após', 'até', 'com', 'contra', 'de', 'desde', 'em', 'entre', 
            'para', 'per', 'perante', 'por', 'sem', 'sob', 'sobre', 'trás',
            'da', 'do', 'das', 'dos', 'na', 'no', 'nas', 'nos', 'pela', 'pelo', 'pelas', 'pelos', 'à', 'às', 'ao', 'aos'
        ]
            
    def create_abbreviation_map(self):
        """
        Acessa um arquivo JSON com informações detalhadas de laboratórios e cria um dicionário de mapeamento.

        Este método carrega um arquivo JSON que contém informações detalhadas sobre laboratórios, incluindo nomes completos,
        CNPJs, abreviações e laboratórios vinculados. Ele então cria um dicionário onde as chaves são as abreviações dos
        laboratórios e os valores são dicionários com as informações detalhadas correspondentes.

        Formato estrutural do arquivo JSON:
        {
            "laboratories": [
                {
                    "full_name": "BIOSINTÉTICA FARMACÊUTICA LTDA",
                    "cnpj": "53162095000106",
                    "abbreviations": ["biosintetica", "bio sintetica"],
                    "linked": ["ACHÉ LABORATÓRIOS FARMACÊUTICOS S.A"]
                },
                {
                    "full_name": "ACHÉ LABORATÓRIOS FARMACÊUTICOS S.A",
                    "cnpj": "60659463002992",
                    "abbreviations": ["ache"]
                },
                ...
            ]
        }

        Returns:
            Dict[str, Dict[str, Any]]: Um dicionário onde cada chave é uma abreviação de laboratório e o valor é um dicionário
            contendo as informações detalhadas do laboratório, como 'full_name', 'cnpj', e 'linked'.
        """
        laboratories = self.labs_json['laboratories']
        abbreviation_map = {}

        for lab in laboratories:
            for abbreviation in lab['abbreviations']:
                abbreviation_normalized = Utils.remove_accents_and_spaces(abbreviation)
                lab_info = {
                    "Name": lab['full_name'],
                    "CNPJ": lab['cnpj']
                }
                linked = lab.get('linked')
                if linked is not None:
                    lab_info['Linked'] = linked
                abbreviation_map[abbreviation_normalized] = lab_info
        
        return abbreviation_map
    
    def process_substances(self):
        """
        Extrai substâncias únicas da coluna 'SUBSTÂNCIA' do DataFrame.
        
        Retorna uma lista ordenada de substâncias únicas, ordenadas por comprimento em ordem decrescente,
        juntamente com o comprimento da substância mais curta encontrada.

        Returns:
            tuple: Uma tupla contendo:
                - sorted_substances (list): Uma lista de substâncias únicas ordenadas por comprimento em ordem decrescente.
                - shortest_length (int): O comprimento da substância mais curta encontrada.
        """
        substances_set = set()
        shortest_length = float('inf')
        
        for row in self.reference_df['SUBSTÂNCIA']:
            if pd.notna(row):
                row_str = str(row)
                if ';' in row_str:
                    substances = row_str.split(';')
                    for substance in substances:
                        substance = substance.strip()
                        substances_set.add(substance)
                        
                        if len(substance) < shortest_length:
                            shortest_length = len(substance)
                else:
                    substance = row_str.strip()
                    substances_set.add(substance)
                    
                    if len(substance) < shortest_length:
                        shortest_length = len(substance)


        return sorted(substances_set, key=len, reverse=True), shortest_length

    
    def get_brand(self, brand):
        """
        Acessa uma coleção de laboratórios e busca informações relevantes de um laboratório específico.

        Este método verifica se o laboratório fornecido está presente na coleção. Se encontrado, retorna um dicionário
        com informações detalhadas sobre o laboratório. Caso contrário, retorna o nome do laboratório fornecido como parâmetro.

        Args:
            brand (str): Nome do laboratório a ser buscado na coleção de laboratórios.
            
        Returns:
            Union[Dict[str, Any], str]: Um dicionário com informações relevantes do laboratório encontrado, ou
            o nome do laboratório fornecido se não for encontrado.
        """
        brand_normalized = Utils.remove_accents_and_spaces(brand)

        if brand_normalized in self.abbreviation_map:
            return self.abbreviation_map[brand_normalized]

        print(f"A marca: {brand} não foi encontrada no banco de dados")
        return brand
    
    def get_filtered_description(self, description):
        """
        Obtém uma descrição filtrada de um medicamento.

        Este método recebe uma descrição de um medicamento como entrada e tenta extrair informações
        relevantes dela, removendo as substâncias conhecidas afim de evitar buscas desnecessárias
        e retornando uma descrição filtrada.

        Args:
            description (str): A descrição do medicamento.

        Returns:
            str: Uma descrição filtrada, contendo apenas informações relevantes sobre o medicamento,
            ou a descrição original se nenhuma informação relevante puder ser extraída.

        Note:
            Este método percorre uma lista de substâncias conhecidas e verifica se elas estão presentes
            na descrição do medicamento. Se uma substância é encontrada na descrição, ela é removida da
            descrição resultante, para evitar processamento desnecessário.

            O método utiliza a normalização de texto para remover acentos e espaços das descrições e das
            substâncias conhecidas antes de realizar a comparação.

            Além disso, ele utiliza um parâmetro `shortest_substance` para determinar o tamanho mínimo
            de uma palavra considerada como uma substância. Isso é útil para evitar a busca por
            substrings muito curtas que não representam substâncias válidas.
        """
        filtered_desc = ''
        description_normalized = Utils.remove_accents_and_spaces(description)
        
        for substance in self.substances_set:
            
            if self.shortest_substance > len(description_normalized):
                break
            
            sub_normalized = Utils.remove_accents_and_spaces(substance)
            if len(sub_normalized) > len(description_normalized):
                continue
            
            if sub_normalized in description_normalized:
                filtered_desc += f'{substance};'
                description_normalized = description_normalized.replace(sub_normalized, '')
                
        if filtered_desc:
            if filtered_desc.endswith(';'):
                filtered_desc = filtered_desc[:-1]
            return filtered_desc
        else:
            for substance in self.substances_set:
                substance_words = [Utils.remove_accents_and_spaces(word) for word in substance.split()]
                substance_words_clean = [word for word in substance_words if len(word) >= self.shortest_substance]
                substance_words_clean = [word for word in substance_words_clean if word not in self.PREPOSITIONS]
                for sub in substance_words_clean:
                    if sub in description_normalized:
                        filtered_desc += f'{sub};'
                        description_normalized = description_normalized.replace(sub, '')
                        
            if filtered_desc:
                if filtered_desc.endswith(';'):
                    filtered_desc = filtered_desc[:-1]
                return filtered_desc
            else:
                return description

    def get_data(self, item_col, desc_col, brand_col):
        """
        Acessa a planilha de medicamentos e filtra as informações relevantes.

        Este método itera sobre cada linha da planilha de medicamentos, tentando obter a descrição
        e o laboratório mais precisos possível para garantir a precisão ao buscar os registros da ANVISA.

        Args:
            item_col (str): Nome exato da coluna referente ao número dos itens da planilha de medicamentos.
            desc_col (str): Nome exato da coluna referente às descrições da planilha de medicamentos.
            brand_col (str): Nome exato da coluna referente aos laboratórios da planilha de medicamentos.
            
        Returns:
            list: Uma lista de dicionários contendo as informações filtradas dos medicamentos. Cada dicionário
                contém as chaves 'item', 'description' e 'brand'.
        """
        data = []
        report_data = []
        for index, row in self.df.iterrows():
            if pd.notna(row[brand_col]):
                brand = self.get_brand(row[brand_col])
                description = self.get_filtered_description(row[desc_col])
                data.append({'item': row[item_col], 'description': description, "brand": brand})
                
                report_data.append({'Item': row[item_col],
                        'Descrição Original': row[desc_col],
                        'Descrição Final': description,
                        'Laboratório Original': row[brand_col],
                        'Laboratório Final': brand if isinstance(brand, str) else brand['Name'],
                        'Registro': '',
                        'PDF': '',
                        'Tempo Decorrido': ''
                        })
                
                
        report_df = pd.DataFrame(report_data)
        report_df.to_excel('relatorio_proc_dados.xlsx', index=False)   
        return data                 