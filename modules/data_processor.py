"""
核心資料處理模組
負責資料載入、清洗、驗證與 KPI 計算
已根據真實 Excel 欄位結構調整：
  精品銷售: DLR, 集團, 零件銷售日, PayCode, 實際售價\n(含稅), 工單號, 品名, 零件料號, 銷售數量
  美容銷售: DLR, 集團, 結算日期, OP_Code, Pay_Code, 金額, 工作單號
  目標資料: DLR Workshop, Jan~Dec
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# ==================== 資料映射字典 ====================
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

# 月份英文對應
MONTH_COLS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


def _infer_group_from_dlr(dlr_code: str) -> str:
    """從 DLR 代碼推斷集團代碼（取前兩碼）"""
    if pd.isna(dlr_code) or not isinstance(dlr_code, str):
        return ''
    return dlr_code[:2].upper()


class DataCleaner:
    """資料清洗類"""

    @staticmethod
    def clean_boutique_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        清洗精品銷售資料
        真實欄位：DLR, 集團, 零件銷售日, PayCode, 實際售價\n(含稅), 工單號, 品名, 零件料號, 銷售數量
        """
        df = df.copy()

        # ── 欄位標準化（去除換行符）──
        df.columns = [str(c).replace('\n', '') for c in df.columns]

        # ── 日期欄位 ──
        # 優先使用「零件銷售日」，其次「結算日期」
        date_col = None
        for c in ['零件銷售日', '結算日期', '日期']:
            if c in df.columns:
                date_col = c
                break
        if date_col:
            df['日期'] = pd.to_datetime(df[date_col], errors='coerce')
        else:
            df['日期'] = pd.NaT

        # ── 銷售金額欄位 ──
        # 優先使用「實際售價(含稅)」，其次「銷售總價(含稅)」
        amount_col = None
        for c in ['實際售價(含稅)', '銷售總價(含稅)', '實際售價\n(含稅)', '銷售總價\n(含稅)', '零售價', '銷售金額']:
            if c in df.columns:
                amount_col = c
                break
        if amount_col:
            df['銷售金額'] = pd.to_numeric(df[amount_col], errors='coerce').fillna(0)
        else:
            df['銷售金額'] = 0.0

        # ── 數量欄位 ──
        qty_col = None
        for c in ['銷售數量', '數量']:
            if c in df.columns:
                qty_col = c
                break
        if qty_col:
            df['數量'] = pd.to_numeric(df[qty_col], errors='coerce').fillna(0)
        else:
            df['數量'] = 1

        # ── 產品名稱 ──
        if '品名' in df.columns:
            df['產品名稱'] = df['品名'].fillna('未知')
        else:
            df['產品名稱'] = '未知'

        # ── 零件號 ──
        if '零件料號' in df.columns:
            df['零件號'] = df['零件料號'].fillna('')
        else:
            df['零件號'] = ''

        # ── PayCode ──
        if 'PayCode' not in df.columns:
            df['PayCode'] = '一般'

        # ── 集團代碼 ──
        # 優先使用「集團」欄位，其次從 DLR 推斷
        if '集團' in df.columns:
            df['Group'] = df['集團'].fillna('')
        elif 'DLR' in df.columns:
            df['Group'] = df['DLR'].apply(_infer_group_from_dlr)
        else:
            df['Group'] = ''

        # ── 集團與經銷商中文名稱 ──
        df['Group_Name'] = df['Group'].map(GROUP_MAPPING).fillna(df['Group'])
        if 'DLR' in df.columns:
            df['DLR_Name'] = df['DLR'].map(DLR_MAPPING).fillna(df['DLR'])
        else:
            df['DLR_Name'] = ''

        # ── 工單號 ──
        if '工單號' not in df.columns:
            df['工單號'] = range(len(df))

        # ── 移除無效日期 ──
        df = df.dropna(subset=['日期'])

        return df

    @staticmethod
    def clean_beauty_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        清洗美容銷售資料
        真實欄位：DLR, 集團, 結算日期, OP_Code, Pay_Code, 金額, 工作單號
        """
        df = df.copy()

        # ── 欄位標準化 ──
        df.columns = [str(c).replace('\n', '') for c in df.columns]

        # ── 日期欄位 ──
        date_col = None
        for c in ['結算日期', '進廠日期', '日期', '結清日期']:
            if c in df.columns:
                date_col = c
                break
        if date_col:
            df['日期'] = pd.to_datetime(df[date_col], errors='coerce')
        else:
            df['日期'] = pd.NaT

        # ── 銷售金額欄位 ──
        amount_col = None
        for c in ['金額', '應收工時費', '銷售金額']:
            if c in df.columns:
                amount_col = c
                break
        if amount_col:
            df['銷售金額'] = pd.to_numeric(df[amount_col], errors='coerce').fillna(0)
        else:
            df['銷售金額'] = 0.0

        # ── OP_Code ──
        if 'OP_Code' not in df.columns:
            for c in ['OP Code', 'OP_CODE', 'op_code']:
                if c in df.columns:
                    df['OP_Code'] = df[c]
                    break
            else:
                df['OP_Code'] = np.nan

        # ── Pay_Code ──
        if 'Pay_Code' not in df.columns:
            for c in ['PayCode', 'PAY_CODE']:
                if c in df.columns:
                    df['Pay_Code'] = df[c]
                    break
            else:
                df['Pay_Code'] = '一般'

        # ── 集團代碼 ──
        if '集團' in df.columns:
            df['Group'] = df['集團'].fillna('')
        elif 'DLR' in df.columns:
            df['Group'] = df['DLR'].apply(_infer_group_from_dlr)
        else:
            df['Group'] = ''

        # ── 集團與經銷商中文名稱 ──
        df['Group_Name'] = df['Group'].map(GROUP_MAPPING).fillna(df['Group'])
        if 'DLR' in df.columns:
            df['DLR_Name'] = df['DLR'].map(DLR_MAPPING).fillna(df['DLR'])
        else:
            df['DLR_Name'] = ''

        # ── 工作單號 ──
        if '工作單號' not in df.columns:
            df['工作單號'] = range(len(df))

        # ── 移除無效日期 ──
        df = df.dropna(subset=['日期'])

        return df

    @staticmethod
    def clean_target_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        清洗年度目標資料
        真實欄位：DLR Workshop, Jan~Dec, Sub TTL
        """
        df = df.copy()

        # ── 欄位標準化 ──
        df.columns = [str(c).replace('\n', '').strip() for c in df.columns]

        # ── DLR 欄位 ──
        if 'DLR Workshop' in df.columns:
            df['DLR'] = df['DLR Workshop'].fillna('')
        elif 'DLR' not in df.columns:
            df['DLR'] = ''

        # ── 從 DLR 推斷集團 ──
        df['Group'] = df['DLR'].apply(_infer_group_from_dlr)
        df['Group_Name'] = df['Group'].map(GROUP_MAPPING).fillna(df['Group'])
        df['DLR_Name'] = df['DLR'].map(DLR_MAPPING).fillna(df['DLR'])

        # ── 月份目標轉換為數值 ──
        for col in MONTH_COLS:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            else:
                df[col] = 0

        # ── 移除空白行 ──
        df = df[df['DLR'].str.len() > 0]

        return df


class DataValidator:
    """資料驗證類（寬鬆模式，符合真實資料）"""

    @staticmethod
    def validate_boutique_data(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """驗證精品銷售資料"""
        errors = []
        # 標準化欄位名
        cols = [str(c).replace('\n', '') for c in df.columns]

        if df.empty:
            errors.append("精品銷售資料為空")
            return False, errors

        # 必要欄位（寬鬆）
        if 'DLR' not in cols:
            errors.append("精品銷售：缺少 DLR 欄位")
        if '工單號' not in cols:
            errors.append("精品銷售：缺少工單號欄位")

        return len(errors) == 0, errors

    @staticmethod
    def validate_beauty_data(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """驗證美容銷售資料"""
        errors = []
        cols = [str(c).replace('\n', '') for c in df.columns]

        if df.empty:
            errors.append("美容銷售資料為空")
            return False, errors

        if 'DLR' not in cols:
            errors.append("美容銷售：缺少 DLR 欄位")
        if '工作單號' not in cols:
            errors.append("美容銷售：缺少工作單號欄位")

        return len(errors) == 0, errors

    @staticmethod
    def validate_target_data(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """驗證目標資料"""
        errors = []
        cols = [str(c).replace('\n', '').strip() for c in df.columns]

        if df.empty:
            errors.append("年度目標資料為空")
            return False, errors

        # 需要 DLR Workshop 或 DLR
        if 'DLR Workshop' not in cols and 'DLR' not in cols:
            errors.append("年度目標：缺少 DLR Workshop 欄位")

        # 需要至少一個月份欄位
        has_month = any(m in cols for m in MONTH_COLS)
        if not has_month:
            errors.append("年度目標：缺少月份目標欄位（Jan~Dec）")

        return len(errors) == 0, errors


class KPICalculator:
    """KPI 計算類"""

    @staticmethod
    def calculate_boutique_penetration(boutique_df: pd.DataFrame) -> float:
        """
        精品滲透率 = 一般銷售總額 / 總工單數
        """
        if boutique_df is None or boutique_df.empty:
            return 0.0

        general_sales = boutique_df[boutique_df['PayCode'] == '一般']['銷售金額'].sum()
        total_jobs = boutique_df['工單號'].nunique()

        return (general_sales / total_jobs) if total_jobs > 0 else 0.0

    @staticmethod
    def calculate_beauty_conversion(beauty_df: pd.DataFrame) -> float:
        """
        美容轉換率 = OP_Code 有值的筆數 / 總工作單號數
        """
        if beauty_df is None or beauty_df.empty:
            return 0.0

        op_count = beauty_df[beauty_df['OP_Code'].notna() & (beauty_df['OP_Code'] != '')].shape[0]
        total_jobs = beauty_df['工作單號'].nunique()

        return (op_count / total_jobs * 100) if total_jobs > 0 else 0.0

    @staticmethod
    def calculate_ytd_metrics(
        actual_df: pd.DataFrame,
        target_df: pd.DataFrame,
        current_date: datetime = None
    ) -> Dict:
        """計算 YTD 指標"""
        if current_date is None:
            current_date = datetime.now()

        current_month = current_date.month
        year_start = datetime(current_date.year, 1, 1)

        ytd_actual = 0.0
        if actual_df is not None and not actual_df.empty and '日期' in actual_df.columns:
            mask = (actual_df['日期'] >= year_start) & (actual_df['日期'] <= current_date)
            ytd_actual = actual_df.loc[mask, '銷售金額'].sum()

        ytd_target = 0.0
        if target_df is not None and not target_df.empty:
            for i, col in enumerate(MONTH_COLS[:current_month], start=1):
                if col in target_df.columns:
                    ytd_target += target_df[col].sum()

        ytd_pct = (ytd_actual / ytd_target * 100) if ytd_target > 0 else 0.0

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
        """計算年度指標"""
        if current_date is None:
            current_date = datetime.now()

        year_start = datetime(current_date.year, 1, 1)

        ytd_actual = 0.0
        if actual_df is not None and not actual_df.empty and '日期' in actual_df.columns:
            mask = (actual_df['日期'] >= year_start) & (actual_df['日期'] <= current_date)
            ytd_actual = actual_df.loc[mask, '銷售金額'].sum()

        annual_target = 0.0
        if target_df is not None and not target_df.empty:
            for col in MONTH_COLS:
                if col in target_df.columns:
                    annual_target += target_df[col].sum()

        annual_pct = (ytd_actual / annual_target * 100) if annual_target > 0 else 0.0

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
        """計算 YoY 對比"""
        if current_date is None:
            current_date = datetime.now()

        current_month = current_date.month

        current_ytd = 0.0
        if current_year_df is not None and not current_year_df.empty:
            year_start = datetime(current_date.year, 1, 1)
            mask = (current_year_df['日期'] >= year_start) & (current_year_df['日期'] <= current_date)
            current_ytd = current_year_df.loc[mask, '銷售金額'].sum()

        previous_ytd = 0.0
        if previous_year_df is not None and not previous_year_df.empty:
            prev_start = datetime(current_date.year - 1, 1, 1)
            prev_end = datetime(current_date.year - 1, current_month, current_date.day)
            mask = (previous_year_df['日期'] >= prev_start) & (previous_year_df['日期'] <= prev_end)
            previous_ytd = previous_year_df.loc[mask, '銷售金額'].sum()

        yoy_pct = ((current_ytd - previous_ytd) / previous_ytd * 100) if previous_ytd > 0 else 0.0

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
        """獲取排名前 N 的產品"""
        if df is None or df.empty:
            return pd.DataFrame()

        # 按產品名稱+零件號分組
        group_cols = ['產品名稱']
        if '零件號' in df.columns:
            group_cols.append('零件號')

        agg = df.groupby(group_cols).agg(
            銷售金額=('銷售金額', 'sum'),
            數量=('數量', 'sum') if '數量' in df.columns else ('銷售金額', 'count')
        ).reset_index()

        sort_col = '銷售金額' if sort_by == 'sales' else '數量'
        return agg.nlargest(top_n, sort_col)

    @staticmethod
    def detect_anomalies(
        current_df: pd.DataFrame,
        previous_df: pd.DataFrame,
        threshold: float = 20.0
    ) -> pd.DataFrame:
        """偵測異常 (YoY 下降 > threshold%)"""
        anomalies = []

        if current_df is None or previous_df is None:
            return pd.DataFrame()
        if current_df.empty or previous_df.empty:
            return pd.DataFrame()
        if '產品名稱' not in current_df.columns:
            return pd.DataFrame()

        current_products = current_df.groupby('產品名稱')['銷售金額'].sum()
        previous_products = previous_df.groupby('產品名稱')['銷售金額'].sum()

        for product in current_products.index:
            if product in previous_products.index:
                cur = current_products[product]
                prev = previous_products[product]
                if prev > 0:
                    decline_pct = ((prev - cur) / prev) * 100
                    if decline_pct > threshold and cur > 1000:
                        anomalies.append({
                            '產品': product,
                            '當年銷售': cur,
                            '去年銷售': prev,
                            '下降百分比': decline_pct
                        })

        if not anomalies:
            return pd.DataFrame()
        return pd.DataFrame(anomalies).sort_values('下降百分比', ascending=False)


class DataProcessor:
    """主要資料處理器"""

    def __init__(self):
        self.boutique_df: Optional[pd.DataFrame] = None
        self.beauty_df: Optional[pd.DataFrame] = None
        self.target_df: Optional[pd.DataFrame] = None
        self.validation_errors: List[str] = []

    def load_data(
        self,
        boutique_path: str,
        beauty_path: str,
        target_path: str
    ) -> Tuple[bool, List[str]]:
        """載入所有資料檔案"""
        self.validation_errors = []

        # ── 精品銷售 ──
        try:
            raw = pd.read_excel(boutique_path)
            is_valid, errors = DataValidator.validate_boutique_data(raw)
            if not is_valid:
                self.validation_errors.extend(errors)
                self.boutique_df = pd.DataFrame()
            else:
                self.boutique_df = DataCleaner.clean_boutique_data(raw)
        except Exception as e:
            self.validation_errors.append(f"精品銷售檔案錯誤: {str(e)}")
            self.boutique_df = pd.DataFrame()

        # ── 美容銷售 ──
        try:
            raw = pd.read_excel(beauty_path)
            is_valid, errors = DataValidator.validate_beauty_data(raw)
            if not is_valid:
                self.validation_errors.extend(errors)
                self.beauty_df = pd.DataFrame()
            else:
                self.beauty_df = DataCleaner.clean_beauty_data(raw)
        except Exception as e:
            self.validation_errors.append(f"美容銷售檔案錯誤: {str(e)}")
            self.beauty_df = pd.DataFrame()

        # ── 年度目標 ──
        try:
            raw = pd.read_excel(target_path)
            is_valid, errors = DataValidator.validate_target_data(raw)
            if not is_valid:
                self.validation_errors.extend(errors)
                self.target_df = pd.DataFrame()
            else:
                self.target_df = DataCleaner.clean_target_data(raw)
        except Exception as e:
            self.validation_errors.append(f"年度目標檔案錯誤: {str(e)}")
            self.target_df = pd.DataFrame()

        return len(self.validation_errors) == 0, self.validation_errors

    def get_boutique_penetration(self) -> float:
        return KPICalculator.calculate_boutique_penetration(self.boutique_df)

    def get_beauty_conversion(self) -> float:
        return KPICalculator.calculate_beauty_conversion(self.beauty_df)

    def filter_by_date_range(
        self,
        df: pd.DataFrame,
        start_date: datetime,
        end_date: datetime
    ) -> pd.DataFrame:
        if df is None or df.empty or '日期' not in df.columns:
            return pd.DataFrame()
        return df[(df['日期'] >= start_date) & (df['日期'] <= end_date)]

    def filter_by_group(self, df: pd.DataFrame, group: str) -> pd.DataFrame:
        if df is None or df.empty or 'Group' not in df.columns:
            return pd.DataFrame()
        return df[df['Group'] == group]

    def filter_by_dlr(self, df: pd.DataFrame, dlr: str) -> pd.DataFrame:
        if df is None or df.empty or 'DLR' not in df.columns:
            return pd.DataFrame()
        return df[df['DLR'] == dlr]
