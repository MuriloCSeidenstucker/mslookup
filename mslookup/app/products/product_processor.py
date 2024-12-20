from mslookup.app.products.product import Product
from mslookup.app.products.medicine import Medicine
from mslookup.app.input_processors.brand_processor import BrandProcessor
from mslookup.app.input_processors.description_processor import DescriptionProcessor
from mslookup.app.input_processors.concentration_processor import ConcentrationProcessor
from mslookup.app.logger_config import get_logger

class ProductProcessor:
    def __init__(self) -> None:
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info('Instantiated.')
        
        self.brand_processor = BrandProcessor()
        self.description_processor = DescriptionProcessor()
        self.concentration_processor = ConcentrationProcessor()

    def get_processed_product(self, product_type: str, item_number: str, description: str, brand: str) -> Product:
        processed_product = None

        if product_type == 'medicine':
            processed_product = self.process_medicine(item_number, description, brand)
        else:
            self.logger.error(f'Unknow product type: {product_type}')
            raise ValueError(f'Unknow product type: {product_type}')

        return processed_product

    def process_medicine(self, item_number: str, description: str, brand: str) -> Medicine:
        processed_brand = self.brand_processor.get_brand(brand)
        concentration = self.concentration_processor.get_concentration(description)
        extracted_substances = self.description_processor.try_get_substances(description)

        processed_medicine = Medicine(
            item_number=item_number,
            description=description,
            brand=processed_brand,
            concentration=concentration,
            extracted_substances=extracted_substances,
        )

        return processed_medicine
