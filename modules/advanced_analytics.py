"""
進階分析模組
提供深度分析功能，包括排名、趨勢分析、異常偵測等
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional


class AdvancedAnalytics:
    """進階分析類"""
    
    @staticmethod
    def get_top_products_by_group(
        df: pd.DataFrame,
        group: str,
        top_n: int = 10,
        metric: str = 'sales'
    ) -> pd.DataFrame:
        """
        按集團獲取排名前 N 的產品
        """
        if df.empty:
            return pd.DataFrame()
        
        group_df = df[df['Group_Name'] == group]
        
        if group_df.empty:
            return pd.DataFrame()
        
        if metric == 'sales':
            return group_df.groupby(['產品名稱', '零件號']).agg({
                '銷售金額': 'sum',
                '數量': 'sum'
            }).reset_index().nlargest(top_n, '銷售金額')
        else:
            return group_df.groupby(['產品名稱', '零件號']).agg({
                '銷售金額': 'sum',
                '數量': 'sum'
            }).reset_index().nlargest(top_n, '數量')
    
    @staticmethod
    def get_top_products_by_dlr(
        df: pd.DataFrame,
        dlr: str,
        top_n: int = 10,
        metric: str = 'sales'
    ) -> pd.DataFrame:
        """
        按經銷商獲取排名前 N 的產品
        """
        if df.empty:
            return pd.DataFrame()
        
        dlr_df = df[df['DLR_Name'] == dlr]
        
        if dlr_df.empty:
            return pd.DataFrame()
        
        if metric == 'sales':
            return dlr_df.groupby(['產品名稱', '零件號']).agg({
                '銷售金額': 'sum',
                '數量': 'sum'
            }).reset_index().nlargest(top_n, '銷售金額')
        else:
            return dlr_df.groupby(['產品名稱', '零件號']).agg({
                '銷售金額': 'sum',
                '數量': 'sum'
            }).reset_index().nlargest(top_n, '數量')
    
    @staticmethod
    def get_group_ranking(
        df: pd.DataFrame,
        metric: str = 'sales',
        top_n: int = 20
    ) -> pd.DataFrame:
        """
        獲取集團排名
        """
        if df.empty:
            return pd.DataFrame()
        
        if metric == 'sales':
            ranking = df.groupby('Group_Name').agg({
                '銷售金額': 'sum',
                '工單號': 'nunique' if '工單號' in df.columns else 'count'
            }).reset_index()
            ranking.columns = ['集團', '銷售金額', '工單數']
        else:
            ranking = df.groupby('Group_Name').agg({
                '數量': 'sum',
                '工單號': 'nunique' if '工單號' in df.columns else 'count'
            }).reset_index()
            ranking.columns = ['集團', '銷售數量', '工單數']
        
        return ranking.sort_values(ranking.columns[1], ascending=False).head(top_n)
    
    @staticmethod
    def get_dlr_ranking(
        df: pd.DataFrame,
        metric: str = 'sales',
        top_n: int = 20
    ) -> pd.DataFrame:
        """
        獲取經銷商排名
        """
        if df.empty:
            return pd.DataFrame()
        
        if metric == 'sales':
            ranking = df.groupby('DLR_Name').agg({
                '銷售金額': 'sum',
                '工單號': 'nunique' if '工單號' in df.columns else 'count'
            }).reset_index()
            ranking.columns = ['經銷商', '銷售金額', '工單數']
        else:
            ranking = df.groupby('DLR_Name').agg({
                '數量': 'sum',
                '工單號': 'nunique' if '工單號' in df.columns else 'count'
            }).reset_index()
            ranking.columns = ['經銷商', '銷售數量', '工單數']
        
        return ranking.sort_values(ranking.columns[1], ascending=False).head(top_n)
    
    @staticmethod
    def get_product_ranking(
        df: pd.DataFrame,
        metric: str = 'sales',
        top_n: int = 20
    ) -> pd.DataFrame:
        """
        獲取產品排名
        """
        if df.empty:
            return pd.DataFrame()
        
        if metric == 'sales':
            ranking = df.groupby(['產品名稱', '零件號']).agg({
                '銷售金額': 'sum',
                '數量': 'sum'
            }).reset_index()
            ranking.columns = ['產品名稱', '零件號', '銷售金額', '銷售數量']
            ranking = ranking.sort_values('銷售金額', ascending=False)
        else:
            ranking = df.groupby(['產品名稱', '零件號']).agg({
                '銷售金額': 'sum',
                '數量': 'sum'
            }).reset_index()
            ranking.columns = ['產品名稱', '零件號', '銷售金額', '銷售數量']
            ranking = ranking.sort_values('銷售數量', ascending=False)
        
        return ranking.head(top_n)
    
    @staticmethod
    def get_monthly_trend(
        df: pd.DataFrame,
        group: Optional[str] = None
    ) -> pd.DataFrame:
        """
        獲取月度趨勢
        """
        if df.empty:
            return pd.DataFrame()
        
        if group:
            df = df[df['Group_Name'] == group]
        
        df['月份'] = df['日期'].dt.to_period('M')
        trend = df.groupby('月份').agg({
            '銷售金額': 'sum',
            '數量': 'sum'
        }).reset_index()
        
        trend['月份'] = trend['月份'].astype(str)
        return trend.sort_values('月份')
    
    @staticmethod
    def get_daily_trend(
        df: pd.DataFrame,
        group: Optional[str] = None
    ) -> pd.DataFrame:
        """
        獲取日度趨勢
        """
        if df.empty:
            return pd.DataFrame()
        
        if group:
            df = df[df['Group_Name'] == group]
        
        trend = df.groupby(df['日期'].dt.date).agg({
            '銷售金額': 'sum',
            '數量': 'sum'
        }).reset_index()
        
        return trend.sort_values('日期')
    
    @staticmethod
    def calculate_growth_rate(
        current_value: float,
        previous_value: float
    ) -> float:
        """
        計算增長率
        """
        if previous_value == 0:
            return 0.0
        return ((current_value - previous_value) / previous_value) * 100
    
    @staticmethod
    def get_product_performance_matrix(
        df: pd.DataFrame,
        metric: str = 'sales'
    ) -> pd.DataFrame:
        """
        獲取產品績效矩陣
        分析產品的銷售金額和銷售數量
        """
        if df.empty:
            return pd.DataFrame()
        
        performance = df.groupby(['產品名稱', '零件號']).agg({
            '銷售金額': 'sum',
            '數量': 'sum'
        }).reset_index()
        
        # 計算平均單價
        performance['平均單價'] = performance['銷售金額'] / performance['數量']
        
        # 計算四分位數
        sales_q1 = performance['銷售金額'].quantile(0.25)
        sales_q3 = performance['銷售金額'].quantile(0.75)
        qty_q1 = performance['數量'].quantile(0.25)
        qty_q3 = performance['數量'].quantile(0.75)
        
        # 分類
        def categorize(row):
            if row['銷售金額'] > sales_q3 and row['數量'] > qty_q3:
                return '明星產品'
            elif row['銷售金額'] > sales_q3 and row['數量'] <= qty_q3:
                return '高價值產品'
            elif row['銷售金額'] <= sales_q3 and row['數量'] > qty_q3:
                return '高銷量產品'
            else:
                return '潛力產品'
        
        performance['分類'] = performance.apply(categorize, axis=1)
        
        return performance.sort_values('銷售金額', ascending=False)
    
    @staticmethod
    def get_customer_concentration(
        df: pd.DataFrame
    ) -> Dict:
        """
        分析客戶集中度
        """
        if df.empty:
            return {}
        
        # 按經銷商分析
        dlr_sales = df.groupby('DLR_Name')['銷售金額'].sum().sort_values(ascending=False)
        total_sales = dlr_sales.sum()
        
        top_3_pct = (dlr_sales.head(3).sum() / total_sales) * 100 if total_sales > 0 else 0
        top_5_pct = (dlr_sales.head(5).sum() / total_sales) * 100 if total_sales > 0 else 0
        
        return {
            'top_3_dlr_pct': top_3_pct,
            'top_5_dlr_pct': top_5_pct,
            'dlr_count': len(dlr_sales),
            'avg_dlr_sales': total_sales / len(dlr_sales) if len(dlr_sales) > 0 else 0
        }
    
    @staticmethod
    def get_sales_distribution(
        df: pd.DataFrame
    ) -> Dict:
        """
        分析銷售分佈
        """
        if df.empty:
            return {}
        
        sales = df['銷售金額']
        
        return {
            'mean': sales.mean(),
            'median': sales.median(),
            'std': sales.std(),
            'min': sales.min(),
            'max': sales.max(),
            'q1': sales.quantile(0.25),
            'q3': sales.quantile(0.75)
        }
    
    @staticmethod
    def identify_slow_movers(
        df: pd.DataFrame,
        threshold_days: int = 30
    ) -> pd.DataFrame:
        """
        識別滯銷產品（最後銷售日期超過 threshold_days）
        """
        if df.empty:
            return pd.DataFrame()
        
        cutoff_date = datetime.now() - timedelta(days=threshold_days)
        
        product_last_sale = df.groupby(['產品名稱', '零件號'])['日期'].max().reset_index()
        product_last_sale.columns = ['產品名稱', '零件號', '最後銷售日期']
        
        slow_movers = product_last_sale[product_last_sale['最後銷售日期'] < cutoff_date]
        
        return slow_movers.sort_values('最後銷售日期')
    
    @staticmethod
    def get_seasonal_pattern(
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        分析季節性模式
        """
        if df.empty:
            return pd.DataFrame()
        
        df['月份'] = df['日期'].dt.month
        seasonal = df.groupby('月份').agg({
            '銷售金額': 'sum',
            '數量': 'sum'
        }).reset_index()
        
        seasonal['月份名'] = seasonal['月份'].map({
            1: '1月', 2: '2月', 3: '3月', 4: '4月',
            5: '5月', 6: '6月', 7: '7月', 8: '8月',
            9: '9月', 10: '10月', 11: '11月', 12: '12月'
        })
        
        return seasonal
