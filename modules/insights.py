import pandas as pd
import numpy as np
from typing import Dict, Any, List

class InsightGenerator:
    """
    Generates automated, structured insights from a dataset
    following the 'What/Why/So What/Now What' format.
    """
    
    @staticmethod
    def get_top_performer(df: pd.DataFrame, cat_col: str = 'Agency Name') -> Dict[str, Any]:
        """Identifies the category with the highest frequency."""
        if df.empty or cat_col not in df.columns:
            return {"name": "N/A", "value": 0}
        
        counts = df[cat_col].value_counts()
        top_name = counts.index[0]
        top_val = counts.values[0]
        return {"name": top_name, "value": top_val}

    @staticmethod
    def get_main_pain_point(df: pd.DataFrame) -> Dict[str, Any]:
        """Identifies the column with the highest missing value count."""
        if df.empty:
            return {"column": "N/A", "count": 0}
            
        null_counts = df.isnull().sum()
        max_null_col = null_counts.idxmax()
        max_null_count = null_counts.max()
        
        return {"column": max_null_col, "count": max_null_count}

    @staticmethod
    def generate_automated_insight(df: pd.DataFrame) -> str:
        """
        Synthesizes data analysis into a structured markdown insight.
        """
        if df.empty:
            return "### 💡 Key Insight\nNo data available to generate insights."

        # 1. Logic for Top Performer (Agency)
        top_agency = InsightGenerator.get_top_performer(df, 'Agency Name')
        
        # 2. Logic for Pain Point (Missing Values)
        pain_point = InsightGenerator.get_main_pain_point(df)
        
        # 3. Time Trend (simple check)
        latest_year = "unknown"
        if 'Vehicle Year' in df.columns:
            latest_year = int(df['Vehicle Year'].max())

        # Constructing the Insight String
        insight = f"""
### 💡 Key Insight
* **What (เกิดอะไรขึ้น):** หน่วยงาน **{top_agency['name']}** มีการบันทึกรายงานอุบัติเหตุสูงสุดที่ **{top_agency['value']:,}** รายการ โดยข้อมูลล่าสุดครอบคลุมถึงปี **{latest_year}**
* **Why (ทำไมถึงเป็นแบบนั้น):** เนื่องจากเป็นหน่วยงานหลักที่มีพื้นที่รับผิดชอบกว้างขวาง หรืออาจมีการเข้มงวดในการกวดขันวินัยจราจรและบันทึกข้อมูลอย่างเป็นระบบมากกว่าหน่วยงานอื่น
* **So What (สำคัญอย่างไร):** พบจุดบกพร่องของข้อมูล (Main Pain Point) ในคอลัมน์ **'{pain_point['column']}'** ซึ่งขาดข้อมูลไปถึง **{pain_point['count']:,}** รายการ ส่งผลให้ความแม่นยำในการวิเคราะห์ภาพรวมลดลง
* **Now What (ทำอะไรต่อ):** แนะนำให้ตรวจสอบระบบการนำเข้าข้อมูลของหน่วยงาน **{top_agency['name']}** เพื่อลดอัตราการว่าง (Missing Values) และจัดสรรงบประมาณสนับสนุนการลงพื้นที่ตรวจสอบในจุดที่เกิดเหตุซ้ำซาก
"""
        return insight.strip()
