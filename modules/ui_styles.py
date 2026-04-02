"""
UI 樣式與主題模組
Volvo 極簡風格 (純白背景)
"""

import streamlit as st
from typing import Dict, Any

# 色彩方案 (Volvo/北歐極簡)
COLORS = {
    'primary': '#003366',      # 深藍
    'secondary': '#0066CC',    # 中藍
    'accent': '#FF6B35',       # 橙色強調
    'success': '#2ECC71',      # 綠色
    'warning': '#F39C12',      # 黃色警告
    'danger': '#E74C3C',       # 紅色危險
    'neutral': '#95A5A6',      # 灰色
    'white': '#FFFFFF',        # 白色
    'light_gray': '#F8F9FA',   # 淺灰
    'dark_gray': '#2C3E50',    # 深灰
}

# 字體設定
FONTS = {
    'chinese': 'Microsoft JhengHei, 微軟正黑體',
    'english': 'Arial, sans-serif',
}

# CSS 樣式
CUSTOM_CSS = f"""
<style>
    /* 全局設定 */
    * {{
        font-family: {FONTS['chinese']}, {FONTS['english']};
    }}
    
    body {{
        background-color: {COLORS['white']};
        color: {COLORS['dark_gray']};
    }}
    
    /* 標題樣式 */
    h1, h2, h3, h4, h5, h6 {{
        color: {COLORS['primary']};
        font-weight: 600;
        letter-spacing: 0.5px;
    }}
    
    h1 {{
        font-size: 2.5rem;
        margin-bottom: 1.5rem;
        border-bottom: 3px solid {COLORS['primary']};
        padding-bottom: 1rem;
    }}
    
    h2 {{
        font-size: 2rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }}
    
    h3 {{
        font-size: 1.5rem;
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
    }}
    
    /* 按鈕樣式 */
    .stButton > button {{
        background-color: {COLORS['primary']};
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }}
    
    .stButton > button:hover {{
        background-color: {COLORS['secondary']};
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
        transform: translateY(-2px);
    }}
    
    /* 側欄樣式 */
    [data-testid="stSidebar"] {{
        background-color: {COLORS['light_gray']};
        border-right: 1px solid #E0E0E0;
    }}
    
    [data-testid="stSidebar"] h2 {{
        color: {COLORS['primary']};
        border-bottom: 2px solid {COLORS['primary']};
        padding-bottom: 0.5rem;
    }}
    
    /* 卡片樣式 */
    .metric-card {{
        background-color: {COLORS['white']};
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }}
    
    .metric-card:hover {{
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border-color: {COLORS['primary']};
    }}
    
    /* 進度條樣式 */
    .progress-bar {{
        background-color: #E0E0E0;
        border-radius: 10px;
        height: 24px;
        overflow: hidden;
    }}
    
    .progress-fill {{
        background: linear-gradient(90deg, {COLORS['primary']}, {COLORS['secondary']});
        height: 100%;
        border-radius: 10px;
        transition: width 0.3s ease;
    }}
    
    /* 表格樣式 */
    .stDataFrame {{
        border-collapse: collapse;
    }}
    
    .stDataFrame th {{
        background-color: {COLORS['primary']};
        color: white;
        font-weight: 600;
        padding: 1rem;
        text-align: left;
        border-bottom: 2px solid {COLORS['primary']};
    }}
    
    .stDataFrame td {{
        padding: 0.75rem 1rem;
        border-bottom: 1px solid #E0E0E0;
    }}
    
    .stDataFrame tr:hover {{
        background-color: {COLORS['light_gray']};
    }}
    
    /* 警告訊息樣式 */
    .stAlert {{
        border-radius: 6px;
        padding: 1rem;
        margin: 1rem 0;
    }}
    
    .alert-danger {{
        background-color: #FADBD8;
        border-left: 4px solid {COLORS['danger']};
        color: {COLORS['danger']};
    }}
    
    .alert-warning {{
        background-color: #FCF3CF;
        border-left: 4px solid {COLORS['warning']};
        color: #8B6914;
    }}
    
    .alert-success {{
        background-color: #D5F4E6;
        border-left: 4px solid {COLORS['success']};
        color: #1E8449;
    }}
    
    /* 篩選器樣式 */
    .stSelectbox, .stMultiSelect, .stDateInput {{
        border-radius: 6px;
    }}
    
    /* 數值顯示 */
    .metric-value {{
        font-size: 2.5rem;
        font-weight: 700;
        color: {COLORS['primary']};
        margin: 0.5rem 0;
    }}
    
    .metric-label {{
        font-size: 0.9rem;
        color: {COLORS['neutral']};
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
    }}
    
    .metric-change {{
        font-size: 1rem;
        font-weight: 600;
        margin-top: 0.5rem;
    }}
    
    .metric-change.positive {{
        color: {COLORS['success']};
    }}
    
    .metric-change.negative {{
        color: {COLORS['danger']};
    }}
</style>
"""


def apply_theme():
    """應用自訂主題"""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def get_metric_card_html(
    label: str,
    value: str,
    change: str = None,
    is_positive: bool = True,
    icon: str = "📊"
) -> str:
    """
    生成指標卡片 HTML
    """
    change_html = ""
    if change:
        change_class = "positive" if is_positive else "negative"
        change_symbol = "↑" if is_positive else "↓"
        change_html = f'<div class="metric-change {change_class}">{change_symbol} {change}</div>'
    
    return f"""
    <div class="metric-card">
        <div class="metric-label">{icon} {label}</div>
        <div class="metric-value">{value}</div>
        {change_html}
    </div>
    """


def get_progress_bar_html(
    current: float,
    target: float,
    label: str = ""
) -> str:
    """
    生成進度條 HTML
    """
    percentage = min((current / target * 100) if target > 0 else 0, 100)
    remaining = max(target - current, 0)
    
    return f"""
    <div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
            <span style="font-weight: 600;">{label}</span>
            <span style="color: {COLORS['neutral']};">{percentage:.1f}%</span>
        </div>
        <div class="progress-bar">
            <div class="progress-fill" style="width: {percentage}%;"></div>
        </div>
        <div style="font-size: 0.85rem; color: {COLORS['neutral']}; margin-top: 0.25rem;">
            剩餘: NT${remaining:,.0f}
        </div>
    </div>
    """


def get_alert_html(
    message: str,
    alert_type: str = "warning"
) -> str:
    """
    生成警告訊息 HTML
    alert_type: 'danger', 'warning', 'success'
    """
    icon_map = {
        'danger': '🚨',
        'warning': '⚠️',
        'success': '✅'
    }
    
    return f"""
    <div class="stAlert alert-{alert_type}">
        <strong>{icon_map.get(alert_type, '📌')} {alert_type.upper()}</strong><br>
        {message}
    </div>
    """


def create_sidebar_section(title: str):
    """建立側欄區段"""
    st.sidebar.markdown(f"### {title}")
    st.sidebar.divider()


def format_currency(value: float, currency: str = "NT$") -> str:
    """格式化貨幣"""
    return f"{currency}{value:,.0f}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """格式化百分比"""
    return f"{value:.{decimals}f}%"


def format_number(value: float, decimals: int = 0) -> str:
    """格式化數字"""
    return f"{value:,.{decimals}f}"


# 預設配置
DEFAULT_CONFIG = {
    'theme': 'light',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded',
    'menu_items': {
        'Get Help': 'https://help.manus.im',
        'Report a bug': 'https://help.manus.im',
        'About': '銷售與美容儀表板 v1.0'
    }
}
