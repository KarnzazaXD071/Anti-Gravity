import pandas as pd
import numpy as np
import datetime
from typing import Dict, Any, List

def run_audit(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Performs a detailed data quality audit and returns results including
    column-level statistics, health scores, and textual summaries.
    """
    total_rows = len(df)
    results = {
        'column_stats': [],
        'scores': {},
        'summary': [],
        'latest_date': 'N/A'
    }

    if df.empty:
        return results

    # 1. Timeliness Check: Latest date
    if 'Crash Date/Time' in df.columns:
        latest = pd.to_datetime(df['Crash Date/Time']).max()
        results['latest_date'] = latest.strftime("%Y-%m-%d %H:%M:%S")

    # 2. Key Fields for Completeness
    key_fields = ['Report Number', 'Local Case Number', 'Agency Name', 'Crash Date/Time']
    
    # Audit Loop
    completeness_metrics = []
    accuracy_issues_count = 0
    
    current_year = datetime.datetime.now().year
    now = datetime.datetime.now()

    for col in df.columns:
        missing_count = df[col].isnull().sum()
        missing_pct = (missing_count / total_rows) * 100
        unique_vals = df[col].nunique()
        dtype = str(df[col].dtype)
        
        # Status Logic
        status = "Valid"
        if col in key_fields and missing_pct > 1:
            status = "Critical"
            results['summary'].append(f"Key field '{col}' exceeds 1% missing threshold ({missing_pct:.2f}%).")
        elif missing_pct > 10:
            status = "Warning"
            
        results['column_stats'].append({
            'Column Name': col,
            'Type': dtype,
            '% Missing': f"{missing_pct:.2f}%",
            'Unique Values': f"{unique_vals:,}",
            'Status': status
        })
        completeness_metrics.append(100 - missing_pct)

    # 3. Consistency Check: Duplicates (Primary Key)
    primary_key = 'Report Number'
    duplicate_count = 0
    if primary_key in df.columns:
        duplicate_count = df.duplicated(subset=[primary_key]).sum()
        duplicate_rate = (duplicate_count / total_rows) * 100
        results['scores']['consistency'] = 100 - duplicate_rate
        if duplicate_count > 0:
            results['summary'].append(f"Found {duplicate_count:,} duplicate IDs based on '{primary_key}'.")
    else:
        results['scores']['consistency'] = 100

    # 4. Accuracy Check: Logical Errors
    # Future dates
    if 'Crash Date/Time' in df.columns:
        future_dates = (pd.to_datetime(df['Crash Date/Time']) > now).sum()
        if future_dates > 0:
            accuracy_issues_count += future_dates
            results['summary'].append(f"Detected {future_dates} records with crashes in the future.")
            
    # Impossible vehicle years
    if 'Vehicle Year' in df.columns:
        invalid_years = (df['Vehicle Year'] > (current_year + 1)).sum()
        if invalid_years > 0:
            accuracy_issues_count += invalid_years
            results['summary'].append(f"Detected {invalid_years} vehicles with years beyond {current_year + 1}.")

    # Negative Speed Limits
    if 'Speed Limit' in df.columns:
        neg_speeds = (df['Speed Limit'] < 0).sum()
        if neg_speeds > 0:
            accuracy_issues_count += neg_speeds
            results['summary'].append(f"Detected {neg_speeds} negative values in Speed Limit.")

    accuracy_rate = (1 - (accuracy_issues_count / (total_rows * 3))) * 100 # Normalized by row count and check count
    results['scores']['accuracy'] = max(0, accuracy_rate)
    results['scores']['completeness'] = sum(completeness_metrics) / len(completeness_metrics)
    
    # Final Health Score (Scoreboard)
    results['health_score'] = (results['scores']['completeness'] + 
                               results['scores']['consistency'] + 
                               results['scores']['accuracy']) / 3

    return results
