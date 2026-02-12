import pandas as pd
import numpy as np
import streamlit as st
from typing import Tuple, List

class DataCleaner:
    """
    Handles interactive data cleaning operations, standardization,
    and logging for the Streamlit application.
    """
    
    @staticmethod
    def get_metrics(df: pd.DataFrame) -> dict:
        """Returns key metrics for before/after comparison."""
        return {
            'row_count': len(df),
            'missing_count': df.isnull().sum().sum(),
            'duplicate_count': df.duplicated().sum()
        }

    @staticmethod
    def impute_column(df: pd.DataFrame, col: str, strategy: str) -> Tuple[pd.DataFrame, str]:
        """
        Applies imputation strategy to a column.
        Strategies: Mean, Median, Mode, Drop.
        """
        msg = ""
        before_nulls = df[col].isnull().sum()
        
        if strategy == "Mean":
            val = df[col].mean()
            df[col] = df[col].fillna(val)
            msg = f"Imputed '{col}' with Mean: {val:.2f}"
        elif strategy == "Median":
            val = df[col].median()
            df[col] = df[col].fillna(val)
            msg = f"Imputed '{col}' with Median: {val:.2f}"
        elif strategy == "Mode":
            val = df[col].mode()[0] if not df[col].mode().empty else "N/A"
            df[col] = df[col].fillna(val)
            msg = f"Imputed '{col}' with Mode: {val}"
        elif strategy == "Drop":
            df = df.dropna(subset=[col])
            msg = f"Dropped {before_nulls} rows with missing values in '{col}'"
            
        return df, msg

    @staticmethod
    def drop_duplicates(df: pd.DataFrame, subset: List[str] = None) -> Tuple[pd.DataFrame, str]:
        """Removes duplicate rows based on subset or all columns."""
        before_count = len(df)
        df = df.drop_duplicates(subset=subset)
        after_count = len(df)
        dropped = before_count - after_count
        msg = f"Removed {dropped} duplicate rows"
        if subset:
            msg += f" based on {subset}"
        return df, msg

    @staticmethod
    def standardize_dates(df: pd.DataFrame, col: str) -> Tuple[pd.DataFrame, str]:
        """Converts string dates to datetime objects."""
        before_count = df[col].isnull().sum()
        df[col] = pd.to_datetime(df[col], errors='coerce')
        after_count = df[col].isnull().sum()
        
        # Report how many failed to parse (became NaT)
        failed = after_count - before_count
        msg = f"Standardized '{col}' to datetime."
        if failed > 0:
            msg += f" (Note: {failed} values failed to parse and were set to NaT)"
            
        return df, msg
