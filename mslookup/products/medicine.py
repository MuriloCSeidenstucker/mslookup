from mslookup.products.product import Product


class Medicine(Product):
    def __init__(
        self,
        item_number,
        description,
        brand,
        concentration,
        extracted_substances,
    ) -> None:
        super().__init__(item_number, description, brand)

        self.concentration = concentration
        self.extracted_substances = extracted_substances
