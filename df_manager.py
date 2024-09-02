import os
import pandas as pd

from typing import List

def load_data(excel_path: str, parquet_path: str, skiprows: int = 0, selected_columns: List[str] = None) -> pd.DataFrame:
    if os.path.exists(parquet_path):
        excel_mod_time = os.path.getmtime(excel_path)
        parquet_mod_time = os.path.getmtime(parquet_path)

        if excel_mod_time > parquet_mod_time:
            df = pd.read_excel(excel_path, skiprows=skiprows, usecols=selected_columns)
            df = df.astype(str)
            df.to_parquet(parquet_path)
        else:
            df = pd.read_parquet(parquet_path)
    else:
        df = pd.read_excel(excel_path, skiprows=skiprows, usecols=selected_columns)
        df = df.astype(str)
        df.to_parquet(parquet_path)

    return df