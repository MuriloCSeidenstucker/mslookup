from abc import ABC


class Product(ABC):
    def __init__(self, item_number, description, brand) -> None:
        self.item_number = item_number
        self.description = description
        self.brand = brand

        self.registers = []
