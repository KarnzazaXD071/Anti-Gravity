import pandas as pd
import datetime
from typing import List, Dict, Tuple

class CleaningEngine:
    """
    Handles data cleaning operations and maintains a history log 
    for traceability and repeatability.
    """
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.history: List[Dict] = []

    def log_step(self, operation: str, impact: str):
        """Adds an entry to the cleaning history log."""
        self.history.append({
            'Timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'Operation': operation,
            'Impact': impact
        })

    def drop_nulls(self, columns: List[str]) -> pd.DataFrame:
        """Drops rows with null values in specified columns."""
        before = len(self.df)
        self.df.dropna(subset=columns, inplace=True)
        after = len(self.df)
        self.log_step(f"Drop Nulls in {', '.join(columns)}", f"Removed {before - after} rows.")
        return self.df

    def fill_nulls(self, column: str, value: any) -> pd.DataFrame:
        """Fills null values in a column with a constant."""
        count = self.df[column].isnull().sum()
        self.df[column].fillna(value, inplace=True)
        self.log_step(f"Fill Nulls in {column}", f"Filled {count} values with '{value}'.")
        return self.df

    def filter_by_year(self, column: str, min_year: int) -> pd.DataFrame:
        """Filters dataset by minimum year."""
        before = len(self.df)
        self.df = self.df[self.df[column] >= min_year]
        after = len(self.df)
        self.log_step(f"Filter {column} >= {min_year}", f"Removed {before - after} rows.")
        return self.df

    def get_history(self) -> pd.DataFrame:
        """Returns the history log as a DataFrame."""
        return pd.DataFrame(self.history)
