import pandas as pd
import numpy as np
import streamlit as st
from typing import Dict, Any

class DataQualityAudit:
    """
    Module to perform Data Quality Audit across 4 dimensions:
    Completeness, Accuracy, Consistency, and Timeliness.
    """
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.results = {}

    @st.cache_resource
    def run_all_audits(_self) -> Dict[str, Any]:
        """Runs all 4 audit dimensions and returns the results."""
        _self.results['completeness'] = _self.check_completeness()
        _self.results['accuracy'] = _self.check_accuracy()
        _self.results['consistency'] = _self.check_consistency()
        _self.results['timeliness'] = _self.check_timeliness()
        return _self.results

    def check_completeness(self) -> Dict[str, Any]:
        """Checks for null values and calculates completion percentage."""
        null_counts = self.df.isnull().sum()
        total_rows = len(self.df)
        completeness_ratio = (1 - (null_counts.sum() / (total_rows * len(self.df.columns)))) * 100
        
        return {
            'ratio': completeness_ratio,
            'missing_by_column': null_counts[null_counts > 0].to_dict()
        }

    def check_accuracy(self) -> Dict[str, Any]:
        """Validates data ranges and logical boundaries (e.g., coordinates)."""
        issues = []
        
        # Latitude/Longitude range check
        if 'Latitude' in self.df.columns and 'Longitude' in self.df.columns:
            invalid_coords = self.df[
                (self.df['Latitude'] < -90) | (self.df['Latitude'] > 90) |
                (self.df['Longitude'] < -180) | (self.df['Longitude'] > 180)
            ]
            if not invalid_coords.empty:
                issues.append(f"Found {len(invalid_coords)} rows with invalid GPS coordinates.")

        # Numeric validity (e.g., Speed Limit)
        if 'Speed Limit' in self.df.columns:
            invalid_speed = self.df[(self.df['Speed Limit'] < 0) | (self.df['Speed Limit'] > 100)]
            if not invalid_speed.empty:
                issues.append(f"Found {len(invalid_speed)} rows with suspicious Speed Limit values.")

        return {
            'status': 'Pass' if not issues else 'Warning',
            'issues': issues
        }

    def check_consistency(self) -> Dict[str, Any]:
        """Logic checks between related columns."""
        issues = []
        
        # Crash Date/Time vs Vehicle Year
        if 'Crash Date/Time' in self.df.columns and 'Vehicle Year' in self.df.columns:
            # Simple check: Vehicle year should not be far in the future compared to crash date
            # Allowing +1 for new models released early
            df_temp = self.df.copy()
            df_temp['Crash Year'] = df_temp['Crash Date/Time'].dt.year
            inconsistent = df_temp[df_temp['Vehicle Year'] > (df_temp['Crash Year'] + 1)]
            if not inconsistent.empty:
                issues.append(f"Found {len(inconsistent)} rows where Vehicle Year is ahead of Crash Date.")

        return {
            'status': 'Pass' if not issues else 'Warning',
            'issues': issues
        }

    def check_timeliness(self) -> Dict[str, Any]:
        """Analyzes the freshness and distribution of data."""
        if 'Crash Date/Time' in self.df.columns:
            min_date = self.df['Crash Date/Time'].min()
            max_date = self.df['Crash Date/Time'].max()
            date_range = (max_date - min_date).days
            
            return {
                'data_range_days': date_range,
                'min_date': min_date,
                'max_date': max_date
            }
        return {'status': 'N/A', 'message': 'Crash Date/Time column not found.'}
