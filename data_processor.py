import pandas as pd

class DataProcessor:
    def __init__(self, file_path):
        self.df = pd.read_excel(file_path)

    def get_data(self, item_col, desc_col, brand_col):
        data = []
        for index, row in self.df.iterrows():
            if pd.notna(row[brand_col]):
                data.append({'item': row[item_col], 'description': row[desc_col], 'brand': row[brand_col]})
        return data
