"""
AI 洞察模組
使用 LLM 生成執行摘要、異常偵測與策略建議
"""

import pandas as pd
from typing import Dict, List, Optional
import os
from openai import OpenAI

# 初始化 OpenAI 客戶端
client = OpenAI()


class AIInsightsGenerator:
    """AI 洞察生成器"""
    
    @staticmethod
    def generate_executive_summary(
        boutique_df: pd.DataFrame,
        beauty_df: pd.DataFrame,
        period: str = "本月",
        model: str = "gpt-4.1-mini"
    ) -> str:
        """
        生成執行摘要
        """
        try:
            # 準備統計資料
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
            
            response = client.messages.create(
                model=model,
                max_tokens=500,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            return response.content[0].text
        
        except Exception as e:
            return f"生成摘要失敗: {str(e)}"
    
    @staticmethod
    def detect_anomalies(
        current_df: pd.DataFrame,
        previous_df: pd.DataFrame,
        threshold: float = 20.0,
        model: str = "gpt-4.1-mini"
    ) -> str:
        """
        偵測異常並生成警告
        """
        try:
            anomalies = AIInsightsGenerator._find_anomalies(
                current_df, 
                previous_df, 
                threshold
            )
            
            if not anomalies:
                return "✅ 未發現重大異常"
            
            anomaly_text = "\n".join([
                f"- {a['產品']}: 下降 {a['下降百分比']:.1f}% (當年: NT${a['當年銷售']:,.0f}, 去年: NT${a['去年銷售']:,.0f})"
                for a in anomalies[:5]
            ])
            
            prompt = f"""
            以下是銷售資料中發現的異常（YoY 下降 > {threshold}%）：
            
            {anomaly_text}
            
            請用繁體中文分析這些異常的可能原因，並提供改進建議（不超過 200 字）。
            """
            
            response = client.messages.create(
                model=model,
                max_tokens=400,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            return response.content[0].text
        
        except Exception as e:
            return f"異常偵測失敗: {str(e)}"
    
    @staticmethod
    def generate_boutique_recommendations(
        boutique_df: pd.DataFrame,
        model: str = "gpt-4.1-mini"
    ) -> str:
        """
        生成精品策略建議
        """
        try:
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
            group_sales = boutique_df.groupby('Group_Name')['銷售金額'].sum().sort_values(ascending=False)
            group_text = "\n".join([
                f"- {group}: NT${sales:,.0f}"
                for group, sales in group_sales.head(5).items()
            ])
            
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
            
            response = client.messages.create(
                model=model,
                max_tokens=400,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            return response.content[0].text
        
        except Exception as e:
            return f"生成建議失敗: {str(e)}"
    
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
            stats['boutique_total'] = boutique_df['銷售金額'].sum()
            stats['boutique_jobs'] = boutique_df['工單號'].nunique()
            stats['boutique_avg'] = stats['boutique_total'] / stats['boutique_jobs'] if stats['boutique_jobs'] > 0 else 0
            
            top_group = boutique_df.groupby('Group_Name')['銷售金額'].sum().idxmax()
            stats['top_group'] = top_group
        
        if not beauty_df.empty:
            stats['beauty_total'] = beauty_df['銷售金額'].sum()
            stats['beauty_jobs'] = beauty_df['工作單號'].nunique()
            stats['beauty_avg'] = stats['beauty_total'] / stats['beauty_jobs'] if stats['beauty_jobs'] > 0 else 0
        
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
        
        # 按產品分組
        current_products = current_df.groupby('產品名稱')['銷售金額'].sum()
        previous_products = previous_df.groupby('產品名稱')['銷售金額'].sum()
        
        for product in current_products.index:
            if product in previous_products.index:
                current_sales = current_products[product]
                previous_sales = previous_products[product]
                
                if previous_sales > 0:
                    decline_pct = ((previous_sales - current_sales) / previous_sales) * 100
                    
                    # 只標記高價值產品的下降
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
        """格式化執行摘要"""
        return f"""
        ### 📊 執行摘要
        
        {summary}
        """
    
    @staticmethod
    def format_anomalies(anomalies: str) -> str:
        """格式化異常警告"""
        return f"""
        ### 🚨 異常偵測
        
        {anomalies}
        """
    
    @staticmethod
    def format_recommendations(recommendations: str) -> str:
        """格式化建議"""
        return f"""
        ### 💡 策略建議
        
        {recommendations}
        """
