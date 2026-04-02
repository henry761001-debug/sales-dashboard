# 銷售與汽車美容儀表板

一個專業的 Streamlit 儀表板，用於追蹤銷售與汽車美容服務的關鍵績效指標。

## 功能特性

### 📊 核心功能
- **雙資料來源支援**：支援手動上傳或 Google Drive 同步
- **KPI 追蹤**：精品滲透率、美容轉換率、銷售額等
- **進度條可視化**：年度至今 (YTD) 與年度目標進度
- **多維度分析**：集團、經銷商、產品分析
- **時間篩選**：本月、本季、本年、自訂範圍

### 🎨 設計風格
- **Volvo 極簡風格**：純白背景、專業配色
- **北歐設計元素**：簡潔、高效、優雅
- **響應式佈局**：適應各種螢幕尺寸

### 📈 分析視圖
1. **經銷商/集團分析**
   - 銷售趨勢圖表
   - 集團銷售比較
   - 經銷商排名

2. **產品分析**
   - 按銷售額排名
   - 按數量排名
   - 產品績效追蹤

### 🤖 AI 洞察
- **執行摘要**：自動生成銷售摘要
- **異常偵測**：識別 YoY 下降 > 20% 的產品
- **策略建議**：基於資料的精品策略建議

### 📥 匯出功能
- **Excel 匯出**：下載篩選後的資料
- **圖表匯出**：保存分析圖表為圖片
- **報告生成**：生成完整的銷售報告

## 資料結構

### 必要檔案
1. **Boutique_Raw.xlsx** - 精品銷售資料
   - 欄位：工單號、PayCode、DLR、Group、產品名稱、零件號、銷售金額、數量、日期

2. **Beauty_Raw.xlsx** - 美容銷售資料
   - 欄位：工作單號、OP_Code、DLR、Group、產品名稱、零件號、銷售金額、數量、日期

3. **Target_2026.xlsx** - 年度目標
   - 欄位：DLR、Group、Month1-Month12

### 資料映射

#### 集團代碼
| 代碼 | 名稱 |
|------|------|
| AM | 新凱 |
| JL | 凱銳北區 |
| KT | 凱桃 |
| YS | 揚昇 |
| SL | 上立 |
| FW | 富王 |
| VM | 匯勝 |
| HC | 匯承 |
| JS | 凱銳南區 |

#### 經銷商代碼
| 代碼 | 名稱 |
|------|------|
| AMA | 新凱內湖 |
| AMC | 新凱仁愛 |
| AMD | 新凱士林 |
| JLA | 凱銳中和 |
| JLB | 凱銳新莊 |
| KTA | 凱桃桃園 |
| KTB | 凱桃中立 |
| YSA | 揚昇新竹 |
| SLA | 上立公益 |
| SLC | 上立崇德 |
| FWA | 富王花壇 |
| FWB | 富王彰化 |
| FWE | 富王草屯 |
| VMA | 匯勝永康 |
| VMB | 匯勝中華 |
| VMC | 匯勝嘉義 |
| HCA | 匯承宜蘭 |
| HCB | 匯承濱江 |
| HCC | 匯承花蓮 |
| JSA | 凱銳博愛 |
| JSB | 凱銳鳳山 |

## 安裝與執行

### 前置要求
- Python 3.11+
- pip3

### 安裝依賴
```bash
pip3 install streamlit pandas openpyxl plotly google-auth-oauthlib google-auth-httplib2 google-api-python-client python-dotenv pillow kaleido openai
```

### 執行儀表板
```bash
streamlit run app.py
```

儀表板將在 `http://localhost:8501` 開啟

### 生成測試資料
```bash
python3.11 generate_sample_data.py
```

## Google Drive 同步設定

### 1. 建立 Google Cloud 專案
1. 前往 [Google Cloud Console](https://console.cloud.google.com)
2. 建立新專案
3. 啟用 Google Drive API
4. 建立 OAuth 2.0 認證（桌面應用程式）
5. 下載認證 JSON 檔案

### 2. 設定認證
將認證 JSON 檔案放在：
```
/home/ubuntu/sales_dashboard/.google_credentials.json
```

### 3. 資料夾 ID
Google Drive 資料夾 ID：`1fXfFrPuorPb77H95ISjeiKppVFgMlDul`

## 專案結構

```
sales_dashboard/
├── app.py                      # 主應用程式
├── generate_sample_data.py     # 測試資料生成
├── README.md                   # 本文件
├── .streamlit/
│   └── config.toml            # Streamlit 配置
├── modules/
│   ├── __init__.py
│   ├── data_processor.py       # 資料處理核心
│   ├── google_drive_sync.py    # Google Drive 同步
│   ├── ui_styles.py            # UI 樣式與主題
│   ├── export_utils.py         # 匯出與圖表生成
│   └── ai_insights.py          # AI 洞察模組
├── data/                       # 資料檔案目錄
├── temp_uploads/              # 臨時上傳檔案
└── temp_exports/              # 臨時匯出檔案
```

## KPI 定義

### 精品滲透率
```
精品滲透率 = 一般銷售總額 / 總工單數
```

### 美容轉換率
```
美容轉換率 = OP_Code 計數 / 總工作單號數 × 100%
```

### YTD 進度
```
YTD % = (實際 Jan-to-Date) / (目標 Jan-to-Date) × 100%
```

### 年度進度
```
年度 % = (實際 Jan-to-Date) / (全年目標) × 100%
```

## 故障排除

### 問題：Google Drive 認證失敗
**解決方案**：
1. 確認認證 JSON 檔案位置正確
2. 檢查 API 是否已啟用
3. 清除舊的 token：`rm /home/ubuntu/sales_dashboard/.google_drive_token.pickle`

### 問題：資料載入失敗
**解決方案**：
1. 檢查檔案名稱是否完全匹配
2. 確認 Excel 檔案格式正確
3. 驗證必要欄位是否存在

### 問題：AI 洞察生成失敗
**解決方案**：
1. 確認 OpenAI API Key 已設定
2. 檢查網路連線
3. 確認 API 配額充足

## 效能優化

- **資料快取**：使用 Streamlit 快取機制減少重複計算
- **增量更新**：支援增量資料同步
- **非同步處理**：AI 洞察使用非同步生成

## 安全性

- **認證管理**：Google Drive token 安全儲存
- **資料驗證**：所有輸入資料驗證
- **錯誤處理**：完善的異常處理機制

## 支援

如有問題或建議，請提交至：https://help.manus.im

## 版本

- **版本**：1.0
- **最後更新**：2026-04-03
- **開發者**：Manus AI

## 授權

本專案為內部使用。

---

**祝您使用愉快！** 📊✨
