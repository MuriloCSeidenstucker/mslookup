from typing import Dict, List, Union

from mslookup.app.products.product import Product
from mslookup.app.products.medicine import Medicine
from mslookup.app.search_in_smerp import SearchInSmerp
from mslookup.app.search_in_open_data_anvisa import OpenDataAnvisa
from mslookup.app.logger_config import get_logger

class SearchProcessor:
    def __init__(self) -> None:
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info('Instantiated.')
        
        self.anvisa_search = OpenDataAnvisa()
        self.smerp_search = SearchInSmerp()

    # Consegue obter registros apenas de medicamentos.
    # Deverá ser estendido no momento da inclusão dos novos tipos de produtos
    def try_get_registrations(self, product: Product) -> List[Dict[str, Union[str, int]]]:
        registrations = []
        if isinstance(product, Medicine):
            registrations = self.get_medicine_registrations(product)

        return registrations

    def get_medicine_registrations(self, medicine: Medicine) -> List[Dict[str, Union[str, int]]]:
        
        description_temp = (
            medicine.extracted_substances
            if medicine.extracted_substances is not None
            else medicine.description
        )
        
        registrations = self.anvisa_search.get_register(
            description_temp, medicine.brand
        )
        
        if not registrations:
            registrations = self.smerp_search.get_data_from_smerp(
                description_temp, medicine.brand
            )

        return registrations
