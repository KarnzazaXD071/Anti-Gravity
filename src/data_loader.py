import streamlit as st
import pandas as pd
import numpy as np
from typing import Optional

@st.cache_data
def load_data(file_path: str) -> pd.DataFrame:
    """
    Loads data from a CSV file with performance optimization.
    
    Args:
        file_path: Absolute path to the CSV file.
        
    Returns:
        pd.DataFrame: The loaded dataset.
    """
    # Optimized for 200k rows
    df = pd.read_csv(file_path, low_memory=False)
    
    # Pre-processing: Convert date columns to datetime
    if 'Crash Date/Time' in df.columns:
        df['Crash Date/Time'] = pd.to_datetime(df['Crash Date/Time'])
    
    return df

def get_data_dictionary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates a data dictionary for the dataset.
    
    Args:
        df: The dataset.
        
    Returns:
        pd.DataFrame: Data dictionary containing column names, types, and sample values.
    """
    data_dict = pd.DataFrame({
        'Column': df.columns,
        'Type': df.dtypes.values,
        'Non-Null Count': df.notnull().sum().values,
        'Sample Value': [df[col].iloc[0] if not df[col].empty else None for col in df.columns]
    })
    return data_dict
