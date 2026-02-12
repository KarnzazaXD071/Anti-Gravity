import streamlit as st
import pandas as pd
import os
from src.data_loader import load_data, get_data_dictionary
from src.quality_audit import DataQualityAudit # Legacy
from src.cleaning_engine import CleaningEngine
from modules.data_audit import run_audit
from modules.cleaning import DataCleaner
from modules.visualization import Visualizer
from modules.insights import InsightGenerator

# Page Config
st.set_page_config(page_title="National Vocational Competition - Data Audit", layout="wide")

# Theme & Styles
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
        font-family: 'Inter', sans-serif;
    }
    .stMetric {
        background-color: black;
        color: black !important;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .health-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: black;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 25px;
    }
    .insight-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #ff7f0e;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .transformation-card {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 5px;
        font-size: 0.8rem;
        border-left: 4px solid #667eea;
    }
    .status-valid { color: #28a745; font-weight: bold; }
    .status-warning { color: #ffc107; font-weight: bold; }
    .status-critical { color: #dc3545; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# App Title
st.title("🛡️ High-Performance Data Quality Guard")
st.caption("National Vocational Competition | Senior Data Engineer Edition")

# Data Loading Progress
DATA_PATH = r"1_crash_reports.csv"

if not os.path.exists(DATA_PATH):
    st.error(f"❌ Data file not found at {DATA_PATH}")
    st.info("💡 Please ensure '1_crash_reports.csv' is in the project root.")
    st.stop()

# Initialize Session State
if 'clean_df' not in st.session_state:
    with st.spinner("🚀 Loading 200k rows with optimized caching..."):
        st.session_state.raw_df = load_data(DATA_PATH)
        st.session_state.clean_df = st.session_state.raw_df.copy()
        st.session_state.engine = CleaningEngine(st.session_state.clean_df)
        st.session_state.cleaning_log = []

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Refined Audit", "Interactive Cleaning", "Analytics Dashboard", "Data Dictionary"])

# Sidebar - Global Filters
st.sidebar.divider()
st.sidebar.subheader("🌍 Global Filters")
with st.sidebar:
    # Filter by Agency
    agencies = sorted(st.session_state.clean_df['Agency Name'].unique().tolist())
    selected_agencies = st.multiselect("Filter by Agency", agencies, default=[])
    
    # Filter by Year
    if 'Vehicle Year' in st.session_state.clean_df.columns:
        years = sorted(st.session_state.clean_df['Vehicle Year'].dropna().unique().astype(int).tolist())
        selected_years = st.multiselect("Filter by Vehicle Year", years, default=[])
    else:
        selected_years = []

# Apply Global Filters to a TEMPORARY dataframe for display
filtered_df = st.session_state.clean_df.copy()
if selected_agencies:
    filtered_df = filtered_df[filtered_df['Agency Name'].isin(selected_agencies)]
if selected_years:
    filtered_df = filtered_df[filtered_df['Vehicle Year'].isin(selected_years)]

# Sidebar - Transformation Steps
st.sidebar.divider()
st.sidebar.subheader("🛤️ Transformation Steps")
if st.session_state.cleaning_log:
    for step in st.session_state.cleaning_log:
        st.sidebar.markdown(f"""<div class="transformation-card">{step}</div>""", unsafe_allow_html=True)
else:
    st.sidebar.info("No transformations applied yet.")

# --- Dashboard ---
if page == "Dashboard":
    st.header("📊 Dataset Overview")
    
    # --- Automated Insight Integration ---
    st.markdown(f"""<div class="insight-card">{InsightGenerator.generate_automated_insight(filtered_df)}</div>""", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Current View Rows", f"{len(filtered_df):,}")
    col2.metric("Total Stats Columns", len(filtered_df.columns))
    
    # Calculate simple completeness for dashboard
    null_ratio = (filtered_df.isnull().sum().sum() / 
                  (len(filtered_df) * len(filtered_df.columns))) if not filtered_df.empty else 1
    col3.metric("Global Completeness", f"{(1-null_ratio)*100:.1f}%")
    col4.metric("Clean Status", "Verified" if not st.session_state.cleaning_log else "Modified")

    st.subheader("Filtered Sample (Top 5)")
    st.dataframe(filtered_df.head(5) if not filtered_df.empty else None)
    
    if filtered_df.empty:
        st.warning("⚠️ No data available under current filters.")

# --- Refined Quality Audit ---
elif page == "Refined Audit":
    st.header("🔎 Advanced Data Health Audit")
    
    with st.spinner("🔍 Running detailed audit..."):
        audit_results = run_audit(filtered_df)
    
    if filtered_df.empty:
        st.warning("Please adjust filters to see audit results.")
    else:
        # Health Scoreboard
        st.markdown(f"""
            <div class="health-card">
                <h2 style="color: white; margin-bottom: 0;">Data Health Score</h2>
                <h1 style="color: white; font-size: 64px; margin-top: 0;">{audit_results['health_score']:.1f}</h1>
                <p style="color: rgba(255,255,255,0.8);">Overall quality metric for current selection</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Metrics Row
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Completeness", f"{audit_results['scores']['completeness']:.1f}%")
        m2.metric("Consistency", f"{audit_results['scores']['consistency']:.1f}%")
        m3.metric("Accuracy", f"{audit_results['scores']['accuracy']:.1f}%")
        m4.metric("Latest Record", audit_results['latest_date'].split(' ')[0])

        # Detailed Table
        st.subheader("📋 Column Quality Status")
        stats_df = pd.DataFrame(audit_results['column_stats'])
        
        def color_status(val):
            color = '#28a745' if val == 'Valid' else '#ffc107' if val == 'Warning' else '#dc3545'
            return f'color: {color}; font-weight: bold'

        st.dataframe(stats_df.style.map(color_status, subset=['Status']), use_container_width=True)

        # Textual Summary
        st.subheader("💬 Audit Summary & Justification")
        if audit_results['summary']:
            for item in audit_results['summary']:
                st.markdown(f"- {item}")
        else:
            st.success("✨ Data is clean! No significant quality issues detected.")

# --- Interactive Cleaning ---
elif page == "Interactive Cleaning":
    st.header("🛠️ Interactive Cleaning Pipeline")
    st.info("💡 Note: Cleaning operations apply to the FULL working dataset, not just the current filtered view.")
    
    # Before Metrics
    st.session_state.before_metrics = DataCleaner.get_metrics(st.session_state.clean_df)
    
    col_input, col_action = st.columns([1, 1])
    
    with col_input:
        st.subheader("Imputation Controls")
        target_col = st.selectbox("Select Target Column", st.session_state.clean_df.columns)
        strategy = st.radio("Imputation Strategy", ["Mean", "Median", "Mode", "Drop"], horizontal=True)
        
        if st.button("🚀 Apply Imputation"):
            st.session_state.clean_df, msg = DataCleaner.impute_column(st.session_state.clean_df, target_col, strategy)
            st.session_state.cleaning_log.append(msg)
            st.success(msg)
            st.rerun()
            
    with col_action:
        st.subheader("Standardization & Formatting")
        date_cols = [c for c in st.session_state.clean_df.columns if 'Date' in c or 'Time' in c]
        date_col = st.selectbox("Select Date Column", date_cols)
        if st.button("📅 Fix Date Formats"):
            st.session_state.clean_df, msg = DataCleaner.standardize_dates(st.session_state.clean_df, date_col)
            st.session_state.cleaning_log.append(msg)
            st.info(msg)
            st.rerun()

        st.subheader("🔗 Referential Integrity")
        if st.button("🗑️ Drop All Duplicates"):
            st.session_state.clean_df, msg = DataCleaner.drop_duplicates(st.session_state.clean_df)
            st.session_state.cleaning_log.append(msg)
            st.success(msg)
            st.rerun()

    st.divider()
    
    # After Metrics
    after_metrics = DataCleaner.get_metrics(st.session_state.clean_df)
    
    st.subheader("⚖️ Before vs After Metrics (Global)")
    c1, c2, c3 = st.columns(3)
    
    def metric_diff(after, before):
        diff = after - before
        return f"{diff:+d}" if diff != 0 else "0"

    c1.metric("Row Count", f"{after_metrics['row_count']:,}", 
              metric_diff(after_metrics['row_count'], st.session_state.before_metrics['row_count']))
    c2.metric("Missing Values", f"{after_metrics['missing_count']:,}", 
              metric_diff(after_metrics['missing_count'], st.session_state.before_metrics['missing_count']),
              delta_color="inverse")
    c3.metric("Duplicates", f"{after_metrics['duplicate_count']:,}", 
              metric_diff(after_metrics['duplicate_count'], st.session_state.before_metrics['duplicate_count']),
              delta_color="inverse")

# --- Analytics Dashboard ---
elif page == "Analytics Dashboard":
    st.header("📈 Interactive Analytics Dashboard")
    
    if filtered_df.empty:
        st.error("No data available for visualization. Please adjust filters.")
    else:
        # --- Automated Insight Integration ---
        st.markdown(f"""<div class="insight-card">{InsightGenerator.generate_automated_insight(filtered_df)}</div>""", unsafe_allow_html=True)

        # Layout
        tab_trend, tab_dist, tab_comp = st.tabs(["🕒 Trend Analysis", "📊 Distributions", "🏢 Comparisons"])
        
        with tab_trend:
            st.subheader("Temporal Trends")
            date_col = 'Crash Date/Time'
            roll_mean = st.toggle("Show 7-Day Rolling Mean", value=False)
            Visualizer.plot_trend(filtered_df, date_col, rolling=roll_mean)
            
        with tab_dist:
            st.subheader("Numerical Distributions")
            num_col = st.selectbox("Select Numeric Feature", ['Speed Limit', 'Vehicle Year', 'Latitude', 'Longitude'])
            hide_outliers = st.toggle("Hide Outliers (Clip to IQR)", value=False)
            Visualizer.plot_distribution(filtered_df, num_col, show_outliers=not hide_outliers)
            
        with tab_comp:
            st.subheader("Categorical Comparisons")
            cat_col = st.selectbox("Select Category", ['Weather', 'Surface Condition', 'Light', 'Collision Type', 'Agency Name'])
            limit = st.slider("Show Top N", 5, 30, 10)
            Visualizer.plot_comparison(filtered_df, cat_col, top_n=limit)

# --- Data Dictionary ---
elif page == "Data Dictionary":
    st.header("📖 Data Dictionary")
    if filtered_df.empty:
        st.warning("⚠️ No data available to generate dictionary. Please adjust filters.")
    else:
        st.markdown("Detailed metadata for compliance with vocational competition standards.")
        dd = get_data_dictionary(filtered_df)
        st.dataframe(dd, use_container_width=True)

# Empty State Global Check
if st.session_state.clean_df.empty:
    st.error("🚨 CRITICAL: The current working dataset is EMPTY.")
    if st.button("Reset Dataset"):
        st.session_state.clean_df = st.session_state.raw_df.copy()
        st.session_state.engine = CleaningEngine(st.session_state.clean_df)
        st.session_state.cleaning_log = []
        st.rerun()
