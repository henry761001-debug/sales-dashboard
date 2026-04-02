"""
測試資料生成工具
生成示例 Excel 檔案用於測試儀表板
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# 資料映射
GROUP_CODES = ['AM', 'JL', 'KT', 'YS', 'SL', 'FW', 'VM', 'HC', 'JS']
DLR_CODES = {
    'AM': ['AMA', 'AMC', 'AMD'],
    'JL': ['JLA', 'JLB'],
    'KT': ['KTA', 'KTB'],
    'YS': ['YSA'],
    'SL': ['SLA', 'SLC'],
    'FW': ['FWA', 'FWB', 'FWE'],
    'VM': ['VMA', 'VMB', 'VMC'],
    'HC': ['HCA', 'HCB', 'HCC'],
    'JS': ['JSA', 'JSB']
}

PRODUCTS_BOUTIQUE = [
    ('機油', 'OIL001'),
    ('濾芯', 'FIL001'),
    ('火星塞', 'SPK001'),
    ('冷卻液', 'COL001'),
    ('輪胎', 'TIR001'),
    ('電池', 'BAT001'),
    ('雨刷', 'WIP001'),
    ('煞車片', 'BRK001'),
    ('空氣濾清器', 'AIR001'),
    ('變速箱油', 'ATF001'),
]

PRODUCTS_BEAUTY = [
    ('洗車服務', 'WASH001'),
    ('打蠟', 'WAX001'),
    ('拋光', 'POL001'),
    ('內飾清潔', 'INT001'),
    ('玻璃膜', 'FILM001'),
    ('隔音', 'SOUND001'),
    ('座椅護理', 'SEAT001'),
    ('輪轂翻新', 'WHEEL001'),
    ('底盤護理', 'UNDER001'),
    ('漆面保護', 'PAINT001'),
]


def generate_boutique_data(num_records=500):
    """生成精品銷售資料"""
    data = []
    
    for i in range(num_records):
        group = random.choice(GROUP_CODES)
        dlr = random.choice(DLR_CODES[group])
        product_name, part_number = random.choice(PRODUCTS_BOUTIQUE)
        
        data.append({
            '工單號': f'BO{datetime.now().year}{i:06d}',
            'PayCode': random.choice(['一般', '特殊']),
            'DLR': dlr,
            'Group': group,
            '產品名稱': product_name,
            '零件號': part_number,
            '銷售金額': random.randint(500, 5000),
            '數量': random.randint(1, 10),
            '日期': datetime.now() - timedelta(days=random.randint(0, 90))
        })
    
    df = pd.DataFrame(data)
    return df


def generate_beauty_data(num_records=400):
    """生成美容銷售資料"""
    data = []
    
    for i in range(num_records):
        group = random.choice(GROUP_CODES)
        dlr = random.choice(DLR_CODES[group])
        product_name, part_number = random.choice(PRODUCTS_BEAUTY)
        
        data.append({
            '工作單號': f'BE{datetime.now().year}{i:06d}',
            'OP_Code': f'OP{random.randint(1000, 9999)}' if random.random() > 0.3 else None,
            'DLR': dlr,
            'Group': group,
            '產品名稱': product_name,
            '零件號': part_number,
            '銷售金額': random.randint(1000, 8000),
            '數量': random.randint(1, 5),
            '日期': datetime.now() - timedelta(days=random.randint(0, 90))
        })
    
    df = pd.DataFrame(data)
    return df


def generate_target_data():
    """生成年度目標資料"""
    data = []
    
    for group in GROUP_CODES:
        for dlr in DLR_CODES[group]:
            row = {
                'DLR': dlr,
                'Group': group,
            }
            
            # 生成 12 個月的目標
            for month in range(1, 13):
                row[f'Month{month}'] = random.randint(50000, 150000)
            
            data.append(row)
    
    df = pd.DataFrame(data)
    return df


def save_sample_data():
    """保存示例資料"""
    print("生成精品銷售資料...")
    boutique_df = generate_boutique_data(500)
    boutique_df.to_excel('/home/ubuntu/sales_dashboard/data/Boutique_Raw.xlsx', index=False)
    print(f"✓ 已保存精品銷售資料 ({len(boutique_df)} 筆)")
    
    print("生成美容銷售資料...")
    beauty_df = generate_beauty_data(400)
    beauty_df.to_excel('/home/ubuntu/sales_dashboard/data/Beauty_Raw.xlsx', index=False)
    print(f"✓ 已保存美容銷售資料 ({len(beauty_df)} 筆)")
    
    print("生成年度目標資料...")
    target_df = generate_target_data()
    target_df.to_excel('/home/ubuntu/sales_dashboard/data/Target_2026.xlsx', index=False)
    print(f"✓ 已保存年度目標資料 ({len(target_df)} 筆)")
    
    print("\n✅ 所有示例資料已生成！")


if __name__ == '__main__':
    save_sample_data()
