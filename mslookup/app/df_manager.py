import os
from pathlib import Path
import sys
from typing import List

import pandas as pd


def load_data(
    excel_path: str,
    parquet_path: str,
    skiprows: int = 0,
    selected_columns: List[str] = None,
) -> pd.DataFrame:
    
    e_path = base_path(excel_path)
    p_path = base_path(parquet_path)
    
    
    if os.path.exists(p_path):
        excel_mod_time = os.path.getmtime(e_path)
        parquet_mod_time = os.path.getmtime(p_path)

        if excel_mod_time > parquet_mod_time:
            df = pd.read_excel(
                e_path, skiprows=skiprows, usecols=selected_columns
            )
            df = df.astype(str)
            df.to_parquet(p_path)
        else:
            df = pd.read_parquet(p_path)
    else:
        df = pd.read_excel(
            e_path, skiprows=skiprows, usecols=selected_columns
        )
        df = df.astype(str)
        df.to_parquet(p_path)

    return df

def base_path(file_path: str):
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return Path(f'{sys._MEIPASS}/{file_path}')
    return Path(file_path)