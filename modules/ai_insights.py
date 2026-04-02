"""
AI 洞察模組
使用 LLM 生成執行摘要、異常偵測與策略建議
"""

import pandas as pd
from typing import Dict, List, Optional
import os


def _get_openai_client():
    """
    延遲初始化 OpenAI 客戶端
    只在需要時才建立，避免模組載入時因缺少 API Key 而報錯
    """
    try:
        from openai import OpenAI
        import streamlit as st

        # 優先從 Streamlit Secrets 取得 API Key
        api_key = None
        try:
            api_key = st.secrets.get("OPENAI_API_KEY", None)
        except Exception:
            pass

        # 其次從環境變數取得
        if not api_key:
            api_key = os.environ.get("OPENAI_API_KEY", None)

        if not api_key:
            raise ValueError(
                "未設定 OpenAI API Key。\n"
                "請在 Streamlit Cloud 的 Secrets 中加入：\n"
                "OPENAI_API_KEY = \"sk-...\""
            )

        return OpenAI(api_key=api_key)

    except ImportError:
        raise ImportError("請安裝 openai 套件：pip install openai")


class AIInsightsGenerator:
    """AI 洞察生成器"""

    @staticmethod
    def generate_executive_summary(
        boutique_df: pd.DataFrame,
        beauty_df: pd.DataFrame,
        period: str = "本月",
        model: str = "gpt-4.1-mini"
    ) -> str:
        """生成執行摘要"""
        try:
            client = _get_openai_client()
            stats = AIInsightsGenerator._prepare_statistics(boutique_df, beauty_df)

            prompt = f"""
            基於以下銷售資料，請生成一份簡潔的執行摘要（繁體中文，不超過 300 字）：

            時期: {period}

            精品銷售:
            - 總銷售額: NT${stats['boutique_total']:,.0f}
            - 工單數: {stats['boutique_jobs']}
            - 平均工單金額: NT${stats['boutique_avg']:,.0f}
            - 頂級集團: {stats['top_group']}

            美容銷售:
            - 總銷售額: NT${stats['beauty_total']:,.0f}
            - 工作單數: {stats['beauty_jobs']}
            - 平均工作單金額: NT${stats['beauty_avg']:,.0f}

            請提供：
            1. 整體銷售表現評估
            2. 主要亮點
            3. 需要關注的領域
            """

            response = client.chat.completions.create(
                model=model,
                max_tokens=600,
                messages=[
                    {"role": "system", "content": "你是一位專業的汽車銷售分析師，擅長分析台灣汽車精品與美容市場。"},
                    {"role": "user", "content": prompt}
                ]
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"⚠️ 生成摘要失敗: {str(e)}"

    @staticmethod
    def detect_anomalies(
        current_df: pd.DataFrame,
        previous_df: pd.DataFrame,
        threshold: float = 20.0,
        model: str = "gpt-4.1-mini"
    ) -> str:
        """偵測異常並生成警告"""
        try:
            anomalies = AIInsightsGenerator._find_anomalies(
                current_df,
                previous_df,
                threshold
            )

            if not anomalies:
                return "✅ 未發現重大異常（YoY 下降超過 20% 的項目）"

            anomaly_text = "\n".join([
                f"- {a['產品']}: 下降 {a['下降百分比']:.1f}% "
                f"(當年: NT${a['當年銷售']:,.0f}, 去年: NT${a['去年銷售']:,.0f})"
                for a in anomalies[:5]
            ])

            client = _get_openai_client()

            prompt = f"""
            以下是銷售資料中發現的異常（YoY 下降 > {threshold}%）：

            {anomaly_text}

            請用繁體中文分析這些異常的可能原因，並提供改進建議（不超過 200 字）。
            """

            response = client.chat.completions.create(
                model=model,
                max_tokens=400,
                messages=[
                    {"role": "system", "content": "你是一位專業的汽車銷售分析師。"},
                    {"role": "user", "content": prompt}
                ]
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"⚠️ 異常偵測失敗: {str(e)}"

    @staticmethod
    def generate_boutique_recommendations(
        boutique_df: pd.DataFrame,
        model: str = "gpt-4.1-mini"
    ) -> str:
        """生成精品策略建議"""
        try:
            client = _get_openai_client()

            # 分析產品類別
            if '產品類別' in boutique_df.columns:
                category_sales = boutique_df.groupby('產品類別')['銷售金額'].sum().sort_values(ascending=False)
                category_text = "\n".join([
                    f"- {cat}: NT${sales:,.0f}"
                    for cat, sales in category_sales.head(5).items()
                ])
            else:
                category_text = "無類別資料"

            # 分析集團表現
            if 'Group_Name' in boutique_df.columns:
                group_sales = boutique_df.groupby('Group_Name')['銷售金額'].sum().sort_values(ascending=False)
                group_text = "\n".join([
                    f"- {group}: NT${sales:,.0f}"
                    for group, sales in group_sales.head(5).items()
                ])
            else:
                group_text = "無集團資料"

            prompt = f"""
            基於以下精品銷售資料，請提供策略建議（繁體中文，不超過 250 字）：

            產品類別銷售排名:
            {category_text}

            集團銷售排名:
            {group_text}

            請提供：
            1. 產品組合優化建議
            2. 集團發展策略
            3. 新產品或新市場機會
            """

            response = client.chat.completions.create(
                model=model,
                max_tokens=400,
                messages=[
                    {"role": "system", "content": "你是一位專業的汽車精品銷售策略顧問。"},
                    {"role": "user", "content": prompt}
                ]
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"⚠️ 生成建議失敗: {str(e)}"

    @staticmethod
    def _prepare_statistics(
        boutique_df: pd.DataFrame,
        beauty_df: pd.DataFrame
    ) -> Dict:
        """準備統計資料"""
        stats = {
            'boutique_total': 0,
            'boutique_jobs': 0,
            'boutique_avg': 0,
            'beauty_total': 0,
            'beauty_jobs': 0,
            'beauty_avg': 0,
            'top_group': '無資料'
        }

        if not boutique_df.empty:
            if '銷售金額' in boutique_df.columns:
                stats['boutique_total'] = boutique_df['銷售金額'].sum()
            if '工單號' in boutique_df.columns:
                stats['boutique_jobs'] = boutique_df['工單號'].nunique()
            if stats['boutique_jobs'] > 0:
                stats['boutique_avg'] = stats['boutique_total'] / stats['boutique_jobs']
            if 'Group_Name' in boutique_df.columns and '銷售金額' in boutique_df.columns:
                try:
                    stats['top_group'] = boutique_df.groupby('Group_Name')['銷售金額'].sum().idxmax()
                except Exception:
                    pass

        if not beauty_df.empty:
            if '銷售金額' in beauty_df.columns:
                stats['beauty_total'] = beauty_df['銷售金額'].sum()
            if '工作單號' in beauty_df.columns:
                stats['beauty_jobs'] = beauty_df['工作單號'].nunique()
            if stats['beauty_jobs'] > 0:
                stats['beauty_avg'] = stats['beauty_total'] / stats['beauty_jobs']

        return stats

    @staticmethod
    def _find_anomalies(
        current_df: pd.DataFrame,
        previous_df: pd.DataFrame,
        threshold: float = 20.0
    ) -> List[Dict]:
        """尋找異常"""
        anomalies = []

        if current_df.empty or previous_df.empty:
            return anomalies

        product_col = '產品名稱' if '產品名稱' in current_df.columns else None
        amount_col = '銷售金額' if '銷售金額' in current_df.columns else None

        if not product_col or not amount_col:
            return anomalies

        current_products = current_df.groupby(product_col)[amount_col].sum()
        previous_products = previous_df.groupby(product_col)[amount_col].sum()

        for product in current_products.index:
            if product in previous_products.index:
                current_sales = current_products[product]
                previous_sales = previous_products[product]

                if previous_sales > 0:
                    decline_pct = ((previous_sales - current_sales) / previous_sales) * 100

                    if decline_pct > threshold and current_sales > 1000:
                        anomalies.append({
                            '產品': product,
                            '當年銷售': current_sales,
                            '去年銷售': previous_sales,
                            '下降百分比': decline_pct
                        })

        return sorted(anomalies, key=lambda x: x['下降百分比'], reverse=True)


class InsightFormatter:
    """洞察格式化器"""

    @staticmethod
    def format_executive_summary(summary: str) -> str:
        return f"### 📊 執行摘要\n\n{summary}"

    @staticmethod
    def format_anomalies(anomalies: str) -> str:
        return f"### 🚨 異常偵測\n\n{anomalies}"

    @staticmethod
    def format_recommendations(recommendations: str) -> str:
        return f"### 💡 策略建議\n\n{recommendations}"
