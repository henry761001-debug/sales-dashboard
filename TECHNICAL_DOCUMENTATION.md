# 技術文件

## 系統架構

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit 前端層                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  側欄配置    │  │  篩選器      │  │  KPI 卡片    │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    業務邏輯層 (Modules)                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ DataProcessor (資料處理)                            │   │
│  │ - 資料驗證、清洗、KPI 計算                          │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ AdvancedAnalytics (進階分析)                        │   │
│  │ - 排名、趨勢、異常偵測                              │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ ChartGenerator (圖表生成)                           │   │
│  │ - Plotly 圖表、匯出功能                             │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ AIInsightsGenerator (AI 洞察)                       │   │
│  │ - LLM 整合、摘要生成                                │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    資料來源層                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  Excel 檔案  │  │ Google Drive  │  │  OpenAI API  │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

---

## 核心模組詳解

### 1. DataProcessor (data_processor.py)

**職責**：資料載入、驗證、清洗與 KPI 計算

**主要類**：
- `DataValidator`：驗證資料完整性
- `DataCleaner`：清洗與標準化資料
- `KPICalculator`：計算關鍵績效指標
- `DataProcessor`：主要協調器

**關鍵方法**：
```python
# 載入資料
processor.load_data(boutique_path, beauty_path, target_path)

# 計算 KPI
penetration = processor.get_boutique_penetration()
conversion = processor.get_beauty_conversion()

# 篩選資料
filtered_df = processor.filter_by_date_range(df, start_date, end_date)
```

**資料流**：
```
Excel 檔案 → 驗證 → 清洗 → 映射 → 快取
```

### 2. AdvancedAnalytics (advanced_analytics.py)

**職責**：深度分析與排名生成

**主要方法**：
- `get_top_products_by_group()`：按集團獲取排名產品
- `get_group_ranking()`：集團排名
- `get_dlr_ranking()`：經銷商排名
- `get_product_ranking()`：產品排名
- `get_monthly_trend()`：月度趨勢
- `identify_slow_movers()`：識別滯銷產品

**複雜度**：O(n log n)（排序操作）

### 3. ChartGenerator (export_utils.py)

**職責**：生成互動式圖表與匯出

**支援的圖表**：
- 銷售趨勢（折線圖）
- 產品排名（橫向柱狀圖）
- 集團/經銷商比較（柱狀圖）
- KPI 進度表（儀表盤）
- 月度對比（柱狀圖）

**技術棧**：
- Plotly：互動式圖表
- Kaleido：圖片匯出
- OpenPyXL：Excel 匯出

### 4. AIInsightsGenerator (ai_insights.py)

**職責**：AI 驅動的洞察生成

**整合**：
- OpenAI API（gpt-4.1-mini）
- 自訂提示工程

**功能**：
1. **執行摘要**：銷售表現評估
2. **異常偵測**：YoY 下降 > 20%
3. **策略建議**：精品優化建議

**提示工程**：
```python
prompt = f"""
基於以下銷售資料，請生成執行摘要：
- 精品銷售：NT${boutique_total:,.0f}
- 美容銷售：NT${beauty_total:,.0f}
...
"""
```

### 5. GoogleDriveSync (google_drive_sync.py)

**職責**：Google Drive 同步與認證

**認證流程**：
```
OAuth 2.0 → Token 快取 → API 呼叫
```

**主要方法**：
- `authenticate()`：OAuth 認證
- `find_file_in_folder()`：查找檔案
- `download_file()`：下載檔案
- `sync_files()`：批量同步

### 6. UIStyles (ui_styles.py)

**設計理念**：Volvo 極簡風格

**配色方案**：
- 主色：#003366（深藍）
- 背景：#FFFFFF（純白）
- 強調：#FF6B35（橙色）

**字體**：
- 中文：Microsoft JhengHei
- 英文：Arial

---

## 資料流

### 1. 初始化流程
```
App 啟動
  ↓
初始化 Session State
  ↓
載入配置
  ↓
應用主題
  ↓
顯示側欄
```

### 2. 資料載入流程
```
用戶選擇資料來源
  ↓
手動上傳 / Google Drive 同步
  ↓
驗證檔案名稱
  ↓
讀取 Excel
  ↓
驗證欄位
  ↓
清洗資料
  ↓
映射代碼
  ↓
快取結果
```

### 3. 分析流程
```
用戶設定篩選器
  ↓
篩選資料
  ↓
計算 KPI
  ↓
生成圖表
  ↓
顯示結果
```

---

## 效能考量

### 1. 快取策略
```python
@st.cache_data
def load_data():
    # 快取資料載入結果
    pass

@st.cache_resource
def init_processor():
    # 快取處理器實例
    pass
```

### 2. 資料優化
- 使用 NumPy 向量化操作
- 避免重複計算
- 按需生成圖表

### 3. 記憶體管理
- 限制資料集大小
- 定期清理臨時檔案
- 使用生成器處理大檔案

---

## 錯誤處理

### 1. 資料驗證錯誤
```python
try:
    success, errors = processor.load_data(...)
    if not success:
        st.error(f"驗證失敗: {errors}")
except Exception as e:
    st.error(f"系統錯誤: {str(e)}")
```

### 2. API 錯誤
```python
try:
    response = client.messages.create(...)
except Exception as e:
    st.warning(f"AI 洞察生成失敗: {str(e)}")
```

### 3. 檔案操作錯誤
```python
try:
    with open(file_path, 'rb') as f:
        content = f.read()
except FileNotFoundError:
    st.error("檔案不存在")
except PermissionError:
    st.error("無權限存取檔案")
```

---

## 安全性

### 1. API 金鑰管理
- 使用環境變數存儲
- 不在代碼中硬編碼
- 定期輪換

### 2. 資料驗證
- 輸入驗證
- 類型檢查
- 範圍檢查

### 3. 存取控制
- 檔案權限設定
- 目錄隔離
- 臨時檔案清理

---

## 擴展性

### 1. 新增資料來源
```python
class NewDataSource:
    def connect(self):
        pass
    
    def fetch_data(self):
        pass
    
    def validate(self):
        pass
```

### 2. 新增分析功能
```python
class NewAnalytics(AdvancedAnalytics):
    @staticmethod
    def new_analysis(df):
        # 新分析邏輯
        pass
```

### 3. 新增圖表類型
```python
def create_new_chart(df):
    fig = go.Figure()
    # 新圖表邏輯
    return fig
```

---

## 測試

### 1. 單元測試
```python
def test_data_validation():
    validator = DataValidator()
    assert validator.validate_boutique_data(df)[0] == True

def test_kpi_calculation():
    calculator = KPICalculator()
    penetration = calculator.calculate_boutique_penetration(df)
    assert penetration > 0
```

### 2. 整合測試
```python
def test_full_pipeline():
    processor = DataProcessor()
    success, errors = processor.load_data(...)
    assert success == True
```

### 3. 效能測試
```python
import time
start = time.time()
# 執行操作
end = time.time()
assert (end - start) < 5  # 應在 5 秒內完成
```

---

## 依賴關係

| 套件 | 版本 | 用途 |
|------|------|------|
| streamlit | 1.28.1 | 前端框架 |
| pandas | 2.3.3 | 資料處理 |
| plotly | 6.3.1 | 圖表生成 |
| openpyxl | 3.1.5 | Excel 讀寫 |
| google-api-python-client | 2.193.0 | Google Drive API |
| openai | 1.3.0 | AI 洞察 |

---

## API 文件

### DataProcessor

```python
class DataProcessor:
    def load_data(boutique_path, beauty_path, target_path) -> Tuple[bool, List[str]]
    def get_boutique_penetration() -> float
    def get_beauty_conversion() -> float
    def filter_by_date_range(df, start_date, end_date) -> pd.DataFrame
```

### AdvancedAnalytics

```python
class AdvancedAnalytics:
    @staticmethod
    def get_top_products_by_group(df, group, top_n=10, metric='sales') -> pd.DataFrame
    @staticmethod
    def get_group_ranking(df, metric='sales', top_n=20) -> pd.DataFrame
    @staticmethod
    def get_product_performance_matrix(df, metric='sales') -> pd.DataFrame
```

### ChartGenerator

```python
class ChartGenerator:
    @staticmethod
    def create_sales_trend_chart(df, title) -> go.Figure
    @staticmethod
    def create_top_products_chart(df, top_n=10, sort_by='sales') -> go.Figure
    @staticmethod
    def create_group_comparison_chart(df, title) -> go.Figure
```

---

## 常見問題

### Q: 如何新增自訂 KPI？
A: 在 `KPICalculator` 中新增方法：
```python
@staticmethod
def calculate_custom_kpi(df):
    # 自訂邏輯
    return result
```

### Q: 如何優化大資料集的效能？
A: 
1. 使用資料篩選減少行數
2. 使用聚合而非詳細資料
3. 啟用快取機制

### Q: 如何整合新的資料來源？
A: 建立新的同步模組並在 `app.py` 中呼叫

---

## 版本控制

- **主版本**：重大功能變更
- **次版本**：新功能或改進
- **修訂版本**：錯誤修復

當前版本：1.0.0

---

**文件版本**：1.0  
**最後更新**：2026-04-03  
**維護者**：Manus AI
