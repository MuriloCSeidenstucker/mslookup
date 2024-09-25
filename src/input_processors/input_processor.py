from typing import Any, Dict, List

import pandas as pd

from src.products.product_processor import ProductProcessor


class InputProcessor:
    def __init__(self, checkpoint_manager):
        self.product_processor = ProductProcessor()

        self.checkpoint_interval = 10
        self.checkpoint_manager = checkpoint_manager

    def read_raw_input(
        self, raw_input: Dict[str, str]
    ) -> List[Dict[str, str]]:
        filtered_input = []
        file_path = raw_input['file_path']
        item_col = raw_input['item_col']
        desc_col = raw_input['desc_col']
        brand_col = raw_input['brand_col']

        df = pd.read_excel(file_path)
        for index, row in df.iterrows():
            if pd.notna(row[brand_col]):
                filtered_input.append(
                    {
                        'item': row[item_col],
                        'description': row[desc_col],
                        'brand': row[brand_col],
                    }
                )

        return filtered_input

    def process_input(self, raw_input: Dict[str, str]) -> List[Dict[str, Any]]:
        filtered_input = self.read_raw_input(raw_input)
        products_type = raw_input['products_type']

        data = []

        current_identifier = self.checkpoint_manager.generate_identifier(
            filtered_input
        )
        checkpoint, saved_identifier = self.checkpoint_manager.load_checkpoint(
            stage='input_processor'
        )
        if saved_identifier == current_identifier:
            data.extend(checkpoint['data'])
            start_index = len(data)
        else:
            start_index = 0

        for index, row in enumerate(filtered_input[start_index:]):

            processed_product = self.product_processor.get_processed_product(
                product_type=products_type,
                item_number=row['item'],
                description=row['description'],
                brand=row['brand'],
            )

            data.append(processed_product)

            if len(data) % self.checkpoint_interval == 0:
                self.checkpoint_manager.save_checkpoint(
                    data, 'input_processor', current_identifier
                )

        self.checkpoint_manager.save_checkpoint(
            data, 'input_processor', current_identifier
        )

        return data
