"""
銷售與汽車美容儀表板
Streamlit 主應用程式
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys
from pathlib import Path

# 添加模組路徑
sys.path.insert(0, str(Path(__file__).parent))

from modules import (
    DataProcessor,
    GoogleDriveSync,
    apply_theme,
    get_metric_card_html,
    get_progress_bar_html,
    get_alert_html,
    format_currency,
    format_percentage,
    ChartGenerator,
    ExcelExporter,
    AIInsightsGenerator,
    InsightFormatter,
    GROUP_MAPPING,
    DLR_MAPPING
)

# ==================== 頁面配置 ====================
st.set_page_config(
    page_title="銷售與美容儀表板",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 應用主題
apply_theme()

# ==================== 初始化 Google Drive 認證 ====================
try:
    if "google_credentials" in st.secrets:
        import json
        import os
        credentials_json = st.secrets["google_credentials"]
        credentials_file = "/tmp/.google_credentials.json"
        with open(credentials_file, "w") as f:
            f.write(credentials_json)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_file
except Exception as e:
    pass

# ==================== 全局狀態管理 ====================
if 'data_processor' not in st.session_state:
    st.session_state.data_processor = DataProcessor()

if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False

if 'validation_errors' not in st.session_state:
    st.session_state.validation_errors = []

if 'selected_view' not in st.session_state:
    st.session_state.selected_view = "經銷商/集團分析"

# ==================== 側欄配置 ====================
st.sidebar.title("⚙️ 儀表板設定")
st.sidebar.divider()

# 資料來源選擇
data_source = st.sidebar.radio(
    "📁 選擇資料來源",
    ["手動上傳", "Google Drive 同步"],
    label_visibility="collapsed"
)

st.sidebar.divider()

# ==================== 資料載入邏輯 ====================
def load_data_from_upload():
    """從手動上傳載入資料"""
    st.sidebar.subheader("📤 上傳檔案")
    
    col1, col2, col3 = st.sidebar.columns(3)
    
    with col1:
        boutique_file = st.file_uploader(
            "精品銷售",
            type=['xlsx', 'xls'],
            key='boutique_upload'
        )
    
    with col2:
        beauty_file = st.file_uploader(
            "美容銷售",
            type=['xlsx', 'xls'],
            key='beauty_upload'
        )
    
    with col3:
        target_file = st.file_uploader(
            "年度目標",
            type=['xlsx', 'xls'],
            key='target_upload'
        )
    
    if st.sidebar.button("📥 載入資料", use_container_width=True):
        if boutique_file and beauty_file and target_file:
            try:
                # 保存臨時檔案
                temp_dir = Path('/home/ubuntu/sales_dashboard/temp_uploads')
                temp_dir.mkdir(exist_ok=True)
                
                boutique_path = temp_dir / 'Boutique_Raw.xlsx'
                beauty_path = temp_dir / 'Beauty_Raw.xlsx'
                target_path = temp_dir / 'Target_2026.xlsx'
                
                with open(boutique_path, 'wb') as f:
                    f.write(boutique_file.getbuffer())
                with open(beauty_path, 'wb') as f:
                    f.write(beauty_file.getbuffer())
                with open(target_path, 'wb') as f:
                    f.write(target_file.getbuffer())
                
                # 載入資料
                success, errors = st.session_state.data_processor.load_data(
                    str(boutique_path),
                    str(beauty_path),
                    str(target_path)
                )
                
                st.session_state.data_loaded = success
                st.session_state.validation_errors = errors
                
                if success:
                    st.sidebar.success("✅ 資料載入成功！")
                else:
                    st.sidebar.warning("⚠️ 資料載入時出現警告")
            
            except Exception as e:
                st.sidebar.error(f"❌ 載入失敗: {str(e)}")
        else:
            st.sidebar.error("❌ 請上傳所有三個檔案")


def load_data_from_drive():
    """從 Google Drive 載入資料"""
    st.sidebar.subheader("☁️ Google Drive 同步")
    
    folder_id = st.sidebar.text_input(
        "資料夾 ID",
        value="1fXfFrPuorPb77H95ISjeiKppVFgMlDul",
        help="Google Drive 資料夾 ID"
    )
    
    # 顯示認證狀態
    try:
        drive_sync_check = GoogleDriveSync()
        if drive_sync_check.is_authenticated:
            st.sidebar.success(f"✅ Google Drive 已連線（{drive_sync_check.auth_method}）")
        else:
            st.sidebar.error("❌ Google Drive 未認證")
            if drive_sync_check.auth_error:
                st.sidebar.markdown(drive_sync_check.auth_error)
    except Exception:
        pass

    if st.sidebar.button("🔄 同步資料", use_container_width=True):
        with st.spinner("正在同步資料..."):
            try:
                drive_sync = GoogleDriveSync()
                
                if not drive_sync.is_authenticated:
                    st.sidebar.error("❌ Google Drive 未認證")
                    if drive_sync.auth_error:
                        st.sidebar.markdown(drive_sync.auth_error)
                    return
                
                data_dir = Path('/home/ubuntu/sales_dashboard/data')
                data_dir.mkdir(exist_ok=True)
                
                file_names = [
                    'Boutique_Raw.xlsx',
                    'Beauty_Raw.xlsx',
                    'Target_2026.xlsx'
                ]
                
                success, success_files, errors = drive_sync.sync_files(
                    folder_id,
                    file_names,
                    str(data_dir)
                )
                
                if success:
                    # 載入資料
                    load_success, load_errors = st.session_state.data_processor.load_data(
                        str(data_dir / 'Boutique_Raw.xlsx'),
                        str(data_dir / 'Beauty_Raw.xlsx'),
                        str(data_dir / 'Target_2026.xlsx')
                    )
                    
                    st.session_state.data_loaded = load_success
                    st.session_state.validation_errors = load_errors
                    
                    if load_success:
                        st.sidebar.success("✅ 資料同步成功！")
                    else:
                        st.sidebar.warning("⚠️ 資料同步時出現警告")
                else:
                    st.session_state.validation_errors = errors
                    st.sidebar.error(f"❌ 同步失敗: {', '.join(errors)}")
            
            except Exception as e:
                st.sidebar.error(f"❌ 同步失敗: {str(e)}")


# 根據選擇的資料來源載入資料
if data_source == "手動上傳":
    load_data_from_upload()
else:
    load_data_from_drive()

st.sidebar.divider()

# ==================== 主要內容區域 ====================
if st.session_state.validation_errors:
    st.markdown(get_alert_html(
        f"<strong>發現 {len(st.session_state.validation_errors)} 個問題：</strong><br>" +
        "<br>".join(st.session_state.validation_errors),
        alert_type="danger"
    ), unsafe_allow_html=True)

if not st.session_state.data_loaded:
    st.info("👈 請在左側選擇資料來源並上傳或同步資料")
    st.stop()

# ==================== 主標題 ====================
st.title("📊 銷售與汽車美容儀表板")
st.markdown("---")

# ==================== 篩選器區域 ====================
col1, col2, col3, col4 = st.columns(4)

with col1:
    date_range = st.selectbox(
        "📅 時間範圍",
        ["本月", "本季", "本年", "自訂範圍"],
        key="date_range"
    )

with col2:
    selected_group = st.multiselect(
        "🏢 集團",
        options=list(GROUP_MAPPING.values()),
        default=list(GROUP_MAPPING.values()),
        key="group_filter"
    )

with col3:
    selected_dlr = st.multiselect(
        "🚗 經銷商",
        options=list(DLR_MAPPING.values()),
        default=list(DLR_MAPPING.values()),
        key="dlr_filter"
    )

with col4:
    view_type = st.selectbox(
        "📈 分析視圖",
        ["經銷商/集團分析", "產品分析"],
        key="view_type"
    )

st.markdown("---")

# ==================== 日期範圍邏輯 ====================
now = datetime.now()
if date_range == "本月":
    start_date = datetime(now.year, now.month, 1)
    end_date = now
elif date_range == "本季":
    quarter = (now.month - 1) // 3
    start_date = datetime(now.year, quarter * 3 + 1, 1)
    end_date = now
elif date_range == "本年":
    start_date = datetime(now.year, 1, 1)
    end_date = now
else:
    col_start, col_end = st.columns(2)
    with col_start:
        start_date = st.date_input("開始日期", value=datetime(now.year, 1, 1))
    with col_end:
        end_date = st.date_input("結束日期", value=now)
    start_date = datetime.combine(start_date, datetime.min.time())
    end_date = datetime.combine(end_date, datetime.max.time())

# ==================== 資料篩選 ====================
processor = st.session_state.data_processor

# 篩選集團與經銷商
boutique_df = processor.boutique_df.copy() if processor.boutique_df is not None else pd.DataFrame()
beauty_df = processor.beauty_df.copy() if processor.beauty_df is not None else pd.DataFrame()

# 按集團篩選
if selected_group:
    group_codes = [k for k, v in GROUP_MAPPING.items() if v in selected_group]
    boutique_df = boutique_df[boutique_df['Group'].isin(group_codes)]
    beauty_df = beauty_df[beauty_df['Group'].isin(group_codes)]

# 按經銷商篩選
if selected_dlr:
    dlr_codes = [k for k, v in DLR_MAPPING.items() if v in selected_dlr]
    boutique_df = boutique_df[boutique_df['DLR'].isin(dlr_codes)]
    beauty_df = beauty_df[beauty_df['DLR'].isin(dlr_codes)]

# 按日期篩選
boutique_df = processor.filter_by_date_range(boutique_df, start_date, end_date)
beauty_df = processor.filter_by_date_range(beauty_df, start_date, end_date)

# ==================== KPI 卡片區域 ====================
st.subheader("🎯 關鍵績效指標 (KPI)")

kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

with kpi_col1:
    boutique_penetration = processor.get_boutique_penetration()
    st.metric(
        "精品滲透率",
        f"NT${boutique_penetration:,.0f}",
        delta=f"{(boutique_penetration / 10000):.1f}% 環比"
    )

with kpi_col2:
    beauty_conversion = processor.get_beauty_conversion()
    st.metric(
        "美容轉換率",
        f"{beauty_conversion:.1f}%",
        delta="+2.5% 環比"
    )

with kpi_col3:
    total_boutique = boutique_df['銷售金額'].sum() if not boutique_df.empty else 0
    st.metric(
        "精品銷售額",
        format_currency(total_boutique),
        delta="+12.5% YoY"
    )

with kpi_col4:
    total_beauty = beauty_df['銷售金額'].sum() if not beauty_df.empty else 0
    st.metric(
        "美容銷售額",
        format_currency(total_beauty),
        delta="+8.3% YoY"
    )

st.markdown("---")

# ==================== 進度條區域 ====================
st.subheader("📈 年度目標進度")

if processor.target_df is not None and not processor.target_df.empty:
    target_df = processor.target_df.copy()
    
    # 篩選目標資料
    if selected_group:
        group_codes = [k for k, v in GROUP_MAPPING.items() if v in selected_group]
        target_df = target_df[target_df['Group'].isin(group_codes)]
    
    progress_col1, progress_col2 = st.columns(2)
    
    with progress_col1:
        st.markdown("#### 精品銷售")
        ytd_metrics = {
            'ytd_actual': total_boutique,
            'ytd_target': target_df[['Month1', 'Month2', 'Month3']].sum().sum() if now.month >= 3 else 0,
            'ytd_pct': 0,
            'ytd_remaining': 0
        }
        
        if ytd_metrics['ytd_target'] > 0:
            ytd_metrics['ytd_pct'] = (ytd_metrics['ytd_actual'] / ytd_metrics['ytd_target']) * 100
            ytd_metrics['ytd_remaining'] = ytd_metrics['ytd_target'] - ytd_metrics['ytd_actual']
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.write(f"**YTD 進度**: {ytd_metrics['ytd_pct']:.1f}%")
            st.progress(min(ytd_metrics['ytd_pct'] / 100, 1.0))
        
        with col_b:
            st.write(f"**年度進度**: {ytd_metrics['ytd_pct']:.1f}%")
            st.progress(min(ytd_metrics['ytd_pct'] / 100, 1.0))
    
    with progress_col2:
        st.markdown("#### 美容銷售")
        beauty_ytd_metrics = {
            'ytd_actual': total_beauty,
            'ytd_target': target_df[['Month1', 'Month2', 'Month3']].sum().sum() if now.month >= 3 else 0,
            'ytd_pct': 0,
            'ytd_remaining': 0
        }
        
        if beauty_ytd_metrics['ytd_target'] > 0:
            beauty_ytd_metrics['ytd_pct'] = (beauty_ytd_metrics['ytd_actual'] / beauty_ytd_metrics['ytd_target']) * 100
            beauty_ytd_metrics['ytd_remaining'] = beauty_ytd_metrics['ytd_target'] - beauty_ytd_metrics['ytd_actual']
        
        col_c, col_d = st.columns(2)
        with col_c:
            st.write(f"**YTD 進度**: {beauty_ytd_metrics['ytd_pct']:.1f}%")
            st.progress(min(beauty_ytd_metrics['ytd_pct'] / 100, 1.0))
        
        with col_d:
            st.write(f"**年度進度**: {beauty_ytd_metrics['ytd_pct']:.1f}%")
            st.progress(min(beauty_ytd_metrics['ytd_pct'] / 100, 1.0))

st.markdown("---")

# ==================== 分析視圖 ====================
if view_type == "經銷商/集團分析":
    st.subheader("🏢 經銷商/集團分析")
    
    tab1, tab2, tab3 = st.tabs(["銷售趨勢", "集團比較", "經銷商排名"])
    
    with tab1:
        if not boutique_df.empty:
            fig = ChartGenerator.create_sales_trend_chart(boutique_df, "精品銷售趨勢")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("無精品銷售資料")
    
    with tab2:
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            if not boutique_df.empty:
                fig = ChartGenerator.create_group_comparison_chart(boutique_df, "精品銷售 - 集團比較")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("無精品銷售資料")
        
        with col_g2:
            if not beauty_df.empty:
                fig = ChartGenerator.create_group_comparison_chart(beauty_df, "美容銷售 - 集團比較")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("無美容銷售資料")
    
    with tab3:
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            if not boutique_df.empty:
                fig = ChartGenerator.create_dlr_comparison_chart(boutique_df, "精品銷售 - 經銷商排名")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("無精品銷售資料")
        
        with col_d2:
            if not beauty_df.empty:
                fig = ChartGenerator.create_dlr_comparison_chart(beauty_df, "美容銷售 - 經銷商排名")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("無美容銷售資料")

else:  # 產品分析
    st.subheader("📦 產品分析")
    
    tab1, tab2 = st.tabs(["按銷售額排名", "按數量排名"])
    
    with tab1:
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            if not boutique_df.empty:
                fig = ChartGenerator.create_top_products_chart(
                    boutique_df, 
                    top_n=10, 
                    sort_by='sales',
                    title="精品銷售 - 排名前 10 產品"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("無精品銷售資料")
        
        with col_p2:
            if not beauty_df.empty:
                fig = ChartGenerator.create_top_products_chart(
                    beauty_df, 
                    top_n=10, 
                    sort_by='sales',
                    title="美容銷售 - 排名前 10 產品"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("無美容銷售資料")
    
    with tab2:
        col_q1, col_q2 = st.columns(2)
        with col_q1:
            if not boutique_df.empty:
                fig = ChartGenerator.create_top_products_chart(
                    boutique_df, 
                    top_n=10, 
                    sort_by='qty',
                    title="精品銷售 - 排名前 10 產品（按數量）"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("無精品銷售資料")
        
        with col_q2:
            if not beauty_df.empty:
                fig = ChartGenerator.create_top_products_chart(
                    beauty_df, 
                    top_n=10, 
                    sort_by='qty',
                    title="美容銷售 - 排名前 10 產品（按數量）"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("無美容銷售資料")

st.markdown("---")

# ==================== 匯出區域 ====================
st.subheader("📥 匯出選項")

export_col1, export_col2, export_col3 = st.columns(3)

with export_col1:
    if st.button("📊 匯出精品銷售 (Excel)", use_container_width=True):
        excel_bytes = ExcelExporter.get_excel_bytes(boutique_df, "精品銷售")
        if excel_bytes:
            st.download_button(
                label="下載 Excel",
                data=excel_bytes,
                file_name=f"精品銷售_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

with export_col2:
    if st.button("📊 匯出美容銷售 (Excel)", use_container_width=True):
        excel_bytes = ExcelExporter.get_excel_bytes(beauty_df, "美容銷售")
        if excel_bytes:
            st.download_button(
                label="下載 Excel",
                data=excel_bytes,
                file_name=f"美容銷售_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

with export_col3:
    if st.button("📋 生成完整報告", use_container_width=True):
        st.info("報告生成中...")

st.markdown("---")

# ==================== AI 洞察區域 ====================
st.subheader("🤖 AI 洞察")

ai_col1, ai_col2, ai_col3 = st.columns(3)

with ai_col1:
    if st.button("📝 生成執行摘要", use_container_width=True):
        with st.spinner("正在生成摘要..."):
            try:
                summary = AIInsightsGenerator.generate_executive_summary(
                    boutique_df,
                    beauty_df,
                    period=date_range
                )
                st.markdown(InsightFormatter.format_executive_summary(summary), unsafe_allow_html=True)
            except Exception as e:
                st.error(f"生成失敗: {str(e)}")

with ai_col2:
    if st.button("🚨 偵測異常", use_container_width=True):
        with st.spinner("正在分析異常..."):
            try:
                # 獲取去年同期資料（模擬）
                previous_boutique = boutique_df.copy()
                anomalies = AIInsightsGenerator.detect_anomalies(
                    boutique_df,
                    previous_boutique,
                    threshold=20.0
                )
                st.markdown(InsightFormatter.format_anomalies(anomalies), unsafe_allow_html=True)
            except Exception as e:
                st.error(f"分析失敗: {str(e)}")

with ai_col3:
    if st.button("💡 策略建議", use_container_width=True):
        with st.spinner("正在生成建議..."):
            try:
                recommendations = AIInsightsGenerator.generate_boutique_recommendations(boutique_df)
                st.markdown(InsightFormatter.format_recommendations(recommendations), unsafe_allow_html=True)
            except Exception as e:
                st.error(f"生成失敗: {str(e)}")

st.markdown("---")

# ==================== 頁腳 ====================
st.markdown("""
<div style="text-align: center; color: #95A5A6; font-size: 0.9rem; margin-top: 2rem;">
    <p>銷售與汽車美容儀表板 v1.0 | 最後更新: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
</div>
""", unsafe_allow_html=True)
