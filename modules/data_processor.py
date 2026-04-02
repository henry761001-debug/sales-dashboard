"""
核心資料處理模組
負責資料載入、清洗、驗證與 KPI 計算
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# 資料映射字典
GROUP_MAPPING = {
    'AM': '新凱',
    'JL': '凱銳北區',
    'KT': '凱桃',
    'YS': '揚昇',
    'SL': '上立',
    'FW': '富王',
    'VM': '匯勝',
    'HC': '匯承',
    'JS': '凱銳南區'
}

DLR_MAPPING = {
    'AMA': '新凱內湖',
    'AMC': '新凱仁愛',
    'AMD': '新凱士林',
    'JLA': '凱銳中和',
    'JLB': '凱銳新莊',
    'KTA': '凱桃桃園',
    'KTB': '凱桃中立',
    'YSA': '揚昇新竹',
    'SLA': '上立公益',
    'SLC': '上立崇德',
    'FWA': '富王花壇',
    'FWB': '富王彰化',
    'FWE': '富王草屯',
    'VMA': '匯勝永康',
    'VMB': '匯勝中華',
    'VMC': '匯勝嘉義',
    'HCA': '匯承宜蘭',
    'HCB': '匯承濱江',
    'HCC': '匯承花蓮',
    'JSA': '凱銳博愛',
    'JSB': '凱銳鳳山'
}


class DataValidator:
    """資料驗證類"""
    
    @staticmethod
    def validate_boutique_data(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """驗證精品銷售資料"""
        errors = []
        required_cols = ['工單號', 'PayCode', 'DLR', 'Group', '銷售金額', '日期']
        
        for col in required_cols:
            if col not in df.columns:
                errors.append(f"缺少必要欄位: {col}")
        
        if df.empty:
            errors.append("精品銷售資料為空")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_beauty_data(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """驗證美容銷售資料"""
        errors = []
        required_cols = ['工作單號', 'OP_Code', 'DLR', 'Group', '銷售金額', '日期']
        
        for col in required_cols:
            if col not in df.columns:
                errors.append(f"缺少必要欄位: {col}")
        
        if df.empty:
            errors.append("美容銷售資料為空")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_target_data(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """驗證目標資料"""
        errors = []
        required_cols = ['DLR', 'Group'] + [f'Month{i}' for i in range(1, 13)]
        
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            errors.append(f"缺少必要欄位: {', '.join(missing_cols)}")
        
        if df.empty:
            errors.append("年度目標資料為空")
        
        return len(errors) == 0, errors


class DataCleaner:
    """資料清洗類"""
    
    @staticmethod
    def clean_boutique_data(df: pd.DataFrame) -> pd.DataFrame:
        """清洗精品銷售資料"""
        df = df.copy()
        
        # 轉換日期格式
        if '日期' in df.columns:
            df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
        
        # 轉換數值
        if '銷售金額' in df.columns:
            df['銷售金額'] = pd.to_numeric(df['銷售金額'], errors='coerce').fillna(0)
        
        # 映射集團與經銷商名稱
        if 'Group' in df.columns:
            df['Group_Name'] = df['Group'].map(GROUP_MAPPING).fillna(df['Group'])
        
        if 'DLR' in df.columns:
            df['DLR_Name'] = df['DLR'].map(DLR_MAPPING).fillna(df['DLR'])
        
        # 移除重複與空值
        df = df.dropna(subset=['工單號', '日期'])
        df = df.drop_duplicates(subset=['工單號', 'DLR'])
        
        return df
    
    @staticmethod
    def clean_beauty_data(df: pd.DataFrame) -> pd.DataFrame:
        """清洗美容銷售資料"""
        df = df.copy()
        
        # 轉換日期格式
        if '日期' in df.columns:
            df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
        
        # 轉換數值
        if '銷售金額' in df.columns:
            df['銷售金額'] = pd.to_numeric(df['銷售金額'], errors='coerce').fillna(0)
        
        # 映射集團與經銷商名稱
        if 'Group' in df.columns:
            df['Group_Name'] = df['Group'].map(GROUP_MAPPING).fillna(df['Group'])
        
        if 'DLR' in df.columns:
            df['DLR_Name'] = df['DLR'].map(DLR_MAPPING).fillna(df['DLR'])
        
        # 移除重複與空值
        df = df.dropna(subset=['工作單號', '日期'])
        df = df.drop_duplicates(subset=['工作單號', 'DLR'])
        
        return df
    
    @staticmethod
    def clean_target_data(df: pd.DataFrame) -> pd.DataFrame:
        """清洗年度目標資料"""
        df = df.copy()
        
        # 映射集團與經銷商名稱
        if 'Group' in df.columns:
            df['Group_Name'] = df['Group'].map(GROUP_MAPPING).fillna(df['Group'])
        
        if 'DLR' in df.columns:
            df['DLR_Name'] = df['DLR'].map(DLR_MAPPING).fillna(df['DLR'])
        
        # 轉換月份目標為數值
        for i in range(1, 13):
            col = f'Month{i}'
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        return df


class KPICalculator:
    """KPI 計算類"""
    
    @staticmethod
    def calculate_boutique_penetration(boutique_df: pd.DataFrame) -> float:
        """
        計算精品滲透率
        = 一般銷售總額 / 總工單數
        """
        if boutique_df.empty:
            return 0.0
        
        general_sales = boutique_df[boutique_df['PayCode'] == '一般']['銷售金額'].sum()
        total_jobs = boutique_df['工單號'].nunique()
        
        if total_jobs == 0:
            return 0.0
        
        return general_sales / total_jobs
    
    @staticmethod
    def calculate_beauty_conversion(beauty_df: pd.DataFrame) -> float:
        """
        計算美容轉換率
        = OP_Code 計數 / 總工作單號數
        """
        if beauty_df.empty:
            return 0.0
        
        op_count = beauty_df[beauty_df['OP_Code'].notna()].shape[0]
        total_jobs = beauty_df['工作單號'].nunique()
        
        if total_jobs == 0:
            return 0.0
        
        return (op_count / total_jobs) * 100
    
    @staticmethod
    def calculate_ytd_metrics(
        actual_df: pd.DataFrame,
        target_df: pd.DataFrame,
        current_date: datetime = None
    ) -> Dict:
        """
        計算年度至今 (YTD) 指標
        """
        if current_date is None:
            current_date = datetime.now()
        
        current_month = current_date.month
        year_start = datetime(current_date.year, 1, 1)
        
        # 篩選 YTD 實際銷售
        ytd_actual = actual_df[
            (actual_df['日期'] >= year_start) & 
            (actual_df['日期'] <= current_date)
        ]['銷售金額'].sum()
        
        # 計算 YTD 目標
        ytd_target = 0
        for i in range(1, current_month + 1):
            col = f'Month{i}'
            if col in target_df.columns:
                ytd_target += target_df[col].sum()
        
        ytd_pct = (ytd_actual / ytd_target * 100) if ytd_target > 0 else 0
        
        return {
            'ytd_actual': ytd_actual,
            'ytd_target': ytd_target,
            'ytd_pct': ytd_pct,
            'ytd_remaining': ytd_target - ytd_actual
        }
    
    @staticmethod
    def calculate_annual_metrics(
        actual_df: pd.DataFrame,
        target_df: pd.DataFrame,
        current_date: datetime = None
    ) -> Dict:
        """
        計算年度指標
        = YTD 實際 / 全年目標
        """
        if current_date is None:
            current_date = datetime.now()
        
        year_start = datetime(current_date.year, 1, 1)
        
        # 篩選 YTD 實際銷售
        ytd_actual = actual_df[
            (actual_df['日期'] >= year_start) & 
            (actual_df['日期'] <= current_date)
        ]['銷售金額'].sum()
        
        # 計算全年目標
        annual_target = 0
        for i in range(1, 13):
            col = f'Month{i}'
            if col in target_df.columns:
                annual_target += target_df[col].sum()
        
        annual_pct = (ytd_actual / annual_target * 100) if annual_target > 0 else 0
        
        return {
            'ytd_actual': ytd_actual,
            'annual_target': annual_target,
            'annual_pct': annual_pct,
            'annual_remaining': annual_target - ytd_actual
        }
    
    @staticmethod
    def calculate_yoy_comparison(
        current_year_df: pd.DataFrame,
        previous_year_df: pd.DataFrame,
        current_date: datetime = None
    ) -> Dict:
        """
        計算年度對比 (YoY)
        """
        if current_date is None:
            current_date = datetime.now()
        
        current_month = current_date.month
        
        # 當年同期
        current_year_start = datetime(current_date.year, 1, 1)
        current_ytd = current_year_df[
            (current_year_df['日期'] >= current_year_start) & 
            (current_year_df['日期'] <= current_date)
        ]['銷售金額'].sum()
        
        # 去年同期
        previous_year_start = datetime(current_date.year - 1, 1, 1)
        previous_year_end = datetime(current_date.year - 1, current_month, 
                                     current_date.day)
        previous_ytd = previous_year_df[
            (previous_year_df['日期'] >= previous_year_start) & 
            (previous_year_df['日期'] <= previous_year_end)
        ]['銷售金額'].sum()
        
        yoy_pct = ((current_ytd - previous_ytd) / previous_ytd * 100) if previous_ytd > 0 else 0
        
        return {
            'current_ytd': current_ytd,
            'previous_ytd': previous_ytd,
            'yoy_pct': yoy_pct,
            'yoy_growth': current_ytd - previous_ytd
        }
    
    @staticmethod
    def get_top_products(
        df: pd.DataFrame,
        top_n: int = 10,
        sort_by: str = 'sales'
    ) -> pd.DataFrame:
        """
        獲取排名前 N 的產品
        sort_by: 'sales' 或 'qty'
        """
        if df.empty:
            return pd.DataFrame()
        
        if sort_by == 'sales':
            return df.nlargest(top_n, '銷售金額')[
                ['產品名稱', '零件號', '銷售金額', '數量']
            ]
        else:
            return df.nlargest(top_n, '數量')[
                ['產品名稱', '零件號', '銷售金額', '數量']
            ]
    
    @staticmethod
    def detect_anomalies(
        current_df: pd.DataFrame,
        previous_df: pd.DataFrame,
        threshold: float = 20.0
    ) -> pd.DataFrame:
        """
        偵測異常 (YoY 下降 > threshold%)
        """
        anomalies = []
        
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
        
        return pd.DataFrame(anomalies).sort_values('下降百分比', ascending=False)


class DataProcessor:
    """主要資料處理器"""
    
    def __init__(self):
        self.boutique_df = None
        self.beauty_df = None
        self.target_df = None
        self.validation_errors = []
    
    def load_data(
        self,
        boutique_path: str,
        beauty_path: str,
        target_path: str
    ) -> Tuple[bool, List[str]]:
        """
        載入所有資料檔案
        """
        self.validation_errors = []
        
        try:
            # 載入精品銷售
            self.boutique_df = pd.read_excel(boutique_path)
            is_valid, errors = DataValidator.validate_boutique_data(self.boutique_df)
            if not is_valid:
                self.validation_errors.extend(errors)
            else:
                self.boutique_df = DataCleaner.clean_boutique_data(self.boutique_df)
        except Exception as e:
            self.validation_errors.append(f"精品銷售檔案錯誤: {str(e)}")
        
        try:
            # 載入美容銷售
            self.beauty_df = pd.read_excel(beauty_path)
            is_valid, errors = DataValidator.validate_beauty_data(self.beauty_df)
            if not is_valid:
                self.validation_errors.extend(errors)
            else:
                self.beauty_df = DataCleaner.clean_beauty_data(self.beauty_df)
        except Exception as e:
            self.validation_errors.append(f"美容銷售檔案錯誤: {str(e)}")
        
        try:
            # 載入年度目標
            self.target_df = pd.read_excel(target_path)
            is_valid, errors = DataValidator.validate_target_data(self.target_df)
            if not is_valid:
                self.validation_errors.extend(errors)
            else:
                self.target_df = DataCleaner.clean_target_data(self.target_df)
        except Exception as e:
            self.validation_errors.append(f"年度目標檔案錯誤: {str(e)}")
        
        return len(self.validation_errors) == 0, self.validation_errors
    
    def get_boutique_penetration(self) -> float:
        """取得精品滲透率"""
        if self.boutique_df is None or self.boutique_df.empty:
            return 0.0
        return KPICalculator.calculate_boutique_penetration(self.boutique_df)
    
    def get_beauty_conversion(self) -> float:
        """取得美容轉換率"""
        if self.beauty_df is None or self.beauty_df.empty:
            return 0.0
        return KPICalculator.calculate_beauty_conversion(self.beauty_df)
    
    def filter_by_date_range(
        self,
        df: pd.DataFrame,
        start_date: datetime,
        end_date: datetime
    ) -> pd.DataFrame:
        """按日期範圍篩選資料"""
        if df is None or df.empty:
            return pd.DataFrame()
        
        return df[
            (df['日期'] >= start_date) & 
            (df['日期'] <= end_date)
        ]
    
    def filter_by_group(
        self,
        df: pd.DataFrame,
        group: str
    ) -> pd.DataFrame:
        """按集團篩選資料"""
        if df is None or df.empty:
            return pd.DataFrame()
        
        return df[df['Group'] == group]
    
    def filter_by_dlr(
        self,
        df: pd.DataFrame,
        dlr: str
    ) -> pd.DataFrame:
        """按經銷商篩選資料"""
        if df is None or df.empty:
            return pd.DataFrame()
        
        return df[df['DLR'] == dlr]
