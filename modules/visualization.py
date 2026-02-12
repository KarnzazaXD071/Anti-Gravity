import pandas as pd
import plotly.express as px
import streamlit as st
from typing import Optional

class Visualizer:
    """
    Module to handle sophisticated data visualizations using Plotly Express,
    with performance optimizations for large datasets.
    """

    @staticmethod
    def sample_data(df: pd.DataFrame, n: int = 10000) -> pd.DataFrame:
        """Samples data if exceeds threshold to prevent rendering lag."""
        if len(df) > 50000:
            return df.sample(n=n, random_state=42)
        return df

    @staticmethod
    def plot_trend(df: pd.DataFrame, date_col: str, rolling: bool = False, window: int = 7):
        """Generates a trend analysis line chart."""
        df_plot = df.copy()
        df_plot[date_col] = pd.to_datetime(df_plot[date_col])
        counts = df_plot.groupby(df_plot[date_col].dt.date).size().reset_index(name='Crash Count')
        counts.columns = ['Date', 'Crash Count']
        
        title = "Crash Trends Over Time"
        if len(df) > 50000:
            title += " (Full Dataset Counted)"
            
        fig = px.line(counts, x='Date', y='Crash Count', title=title, 
                      template="plotly_white", color_discrete_sequence=['#667eea'])
        
        if rolling:
            counts['Rolling Mean'] = counts['Crash Count'].rolling(window=window).mean()
            fig.add_scatter(x=counts['Date'], y=counts['Rolling Mean'], name=f'{window}-Day Rolling Mean',
                            line=dict(color='#ff7f0e', width=3))
            
        fig.update_layout(hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def plot_distribution(df: pd.DataFrame, num_col: str, show_outliers: bool = True):
        """Generates a distribution histogram and boxplot with outlier toggle."""
        df_plot = Visualizer.sample_data(df)
        is_sampled = len(df) > 50000
        
        title = f"Distribution of {num_col}"
        if is_sampled:
            title += " (Sampled 10k rows)"
            
        fig = px.histogram(df_plot, x=num_col, marginal="box", 
                           title=title, template="plotly_white",
                           color_discrete_sequence=['#764ba2'])
        
        if not show_outliers:
            # Simple outlier removal for visualization: Clip to 1.5 * IQR
            q1 = df[num_col].quantile(0.25)
            q3 = df[num_col].quantile(0.75)
            iqr = q3 - q1
            fig.update_xaxes(range=[q1 - 1.5 * iqr, q3 + 1.5 * iqr])
            
        st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def plot_comparison(df: pd.DataFrame, cat_col: str, top_n: int = 10):
        """Generates a bar chart for categorical comparison, sorted descending."""
        counts = df[cat_col].value_counts().reset_index()
        counts.columns = [cat_col, 'Count']
        counts = counts.sort_values(by='Count', ascending=False).head(top_n)
        
        fig = px.bar(counts, x=cat_col, y='Count', title=f"Top {top_n} {cat_col}",
                     color='Count', color_continuous_scale='Viridis',
                     template="plotly_white")
        
        fig.update_layout(xaxis={'categoryorder':'total descending'})
        st.plotly_chart(fig, use_container_width=True)
