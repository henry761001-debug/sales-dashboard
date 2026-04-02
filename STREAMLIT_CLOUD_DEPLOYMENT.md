# Streamlit Cloud 部署指南

## 概述

本指南將幫助您將銷售與汽車美容儀表板部署到 Streamlit Cloud，成為永久網站。

---

## 前置要求

- GitHub 帳戶
- Streamlit 帳戶（可用 GitHub 登入）
- 已完成 Google Drive API 設定（參考 GOOGLE_DRIVE_SETUP.md）

---

## 步驟 1：準備 GitHub 倉庫

### 1.1 建立 GitHub 倉庫

1. 前往 [GitHub](https://github.com/)
2. 登入您的帳戶
3. 點擊「+」→「New repository」
4. 填寫資訊：
   - **Repository name**：`sales-dashboard`
   - **Description**：`銷售與汽車美容儀表板`
   - **Visibility**：`Public`（Streamlit Cloud 需要公開倉庫）
5. 點擊「Create repository」

### 1.2 初始化本地 Git

```bash
cd /home/ubuntu/sales_dashboard

# 初始化 Git
git init

# 添加遠程倉庫
git remote add origin https://github.com/your-username/sales-dashboard.git

# 設定 Git 用戶
git config user.email "your-email@example.com"
git config user.name "Your Name"
```

### 1.3 提交代碼

```bash
# 添加所有檔案
git add .

# 提交
git commit -m "Initial commit: Sales Dashboard v1.0"

# 推送到 GitHub
git branch -M main
git push -u origin main
```

---

## 步驟 2：在 Streamlit Cloud 上部署

### 2.1 前往 Streamlit Cloud

1. 訪問 [Streamlit Cloud](https://share.streamlit.io/)
2. 點擊「New app」

### 2.2 連接 GitHub

1. 點擊「GitHub」
2. 授權 Streamlit 存取您的 GitHub 帳戶
3. 選擇倉庫：`your-username/sales-dashboard`
4. 選擇分支：`main`
5. 選擇檔案路徑：`app.py`

### 2.3 配置應用程式

1. 點擊「Deploy」
2. 等待應用程式部署（通常需要 2-5 分鐘）

---

## 步驟 3：配置 Secrets

### 3.1 訪問應用程式設定

1. 在 Streamlit Cloud 中找到您的應用程式
2. 點擊「Settings」（右上角三點選單）
3. 選擇「Secrets」

### 3.2 添加 Google Drive 認證

在 Secrets 編輯器中粘貼您的 Google Drive 認證 JSON：

```toml
google_credentials = """
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "your-private-key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
  "client_id": "your-client-id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "your-cert-url"
}
"""
```

### 3.3 保存 Secrets

點擊「Save」按鈕

---

## 步驟 4：驗證部署

### 4.1 檢查應用程式狀態

1. 應用程式 URL 格式：`https://share.streamlit.io/your-username/sales-dashboard/main/app.py`
2. 或使用 Streamlit 提供的自訂 URL

### 4.2 測試功能

1. 打開應用程式 URL
2. 在側欄選擇「Google Drive 同步」
3. 輸入資料夾 ID：`1fXfFrPuorPb77H95ISjeiKppVFgMlDul`
4. 點擊「同步資料」
5. 驗證資料是否正確載入

---

## 步驟 5：配置自訂域名（可選）

### 5.1 購買域名

1. 在域名提供商（如 Namecheap、GoDaddy）購買域名
2. 記下您的域名（例如：`dashboard.yourdomain.com`）

### 5.2 配置 DNS

#### 使用 Cloudflare（推薦）

1. 在 [Cloudflare](https://www.cloudflare.com/) 建立帳戶
2. 添加您的域名
3. 更新域名註冊商的 Nameservers 為 Cloudflare 提供的值
4. 在 Cloudflare 中添加 CNAME 記錄：
   - **Name**：`dashboard`（或您想要的子域名）
   - **Target**：`share.streamlit.io`
   - **TTL**：Auto
5. 點擊「Save」

#### 使用標準 DNS

1. 登入您的域名提供商
2. 進入 DNS 設定
3. 添加 CNAME 記錄：
   - **Host**：`dashboard.yourdomain.com`
   - **Points to**：`share.streamlit.io`
4. 保存設定

### 5.3 在 Streamlit Cloud 中配置

1. 在應用程式設定中找到「Custom domain」
2. 輸入您的自訂域名
3. 點擊「Save」

---

## 步驟 6：優化應用程式

### 6.1 更新 app.py 以支援 Secrets

```python
import streamlit as st
import os

# 從 Secrets 讀取 Google Drive 認證
if "google_credentials" in st.secrets:
    credentials_json = st.secrets["google_credentials"]
    credentials_file = "/tmp/.google_credentials.json"
    with open(credentials_file, "w") as f:
        f.write(credentials_json)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_file
```

### 6.2 添加快取以提高效能

```python
@st.cache_data
def load_data_cached():
    # 您的資料載入邏輯
    pass
```

### 6.3 優化記憶體使用

- 限制資料集大小
- 使用資料篩選
- 定期清理臨時檔案

---

## 步驟 7：監控與維護

### 7.1 檢查應用程式日誌

1. 在 Streamlit Cloud 中點擊「Manage app」
2. 查看「Logs」標籤

### 7.2 自動重新部署

- Streamlit Cloud 會自動監視 GitHub 倉庫
- 每當您推送代碼時，應用程式會自動重新部署

### 7.3 更新應用程式

```bash
# 進行更改
# ...

# 提交並推送
git add .
git commit -m "Update: [描述您的更改]"
git push origin main

# Streamlit Cloud 會自動部署
```

---

## 常見問題

### Q: 應用程式無法連接到 Google Drive
**A**: 
1. 檢查 Secrets 中的認證是否正確
2. 確認 Google Drive API 已啟用
3. 驗證資料夾 ID 是否正確
4. 檢查應用程式日誌中的錯誤訊息

### Q: 應用程式很慢
**A**:
1. 啟用快取機制
2. 減少資料集大小
3. 使用資料篩選
4. 優化圖表生成

### Q: 如何更新應用程式？
**A**:
1. 在本地進行更改
2. 提交到 GitHub
3. Streamlit Cloud 會自動部署

### Q: 自訂域名不工作
**A**:
1. 檢查 DNS 記錄是否正確
2. 等待 DNS 傳播（可能需要 24 小時）
3. 使用 `nslookup` 或 `dig` 驗證 DNS 設定
4. 檢查 Streamlit Cloud 中的自訂域名設定

### Q: 如何回滾到舊版本？
**A**:
1. 在 GitHub 中找到舊的 commit
2. 點擊「Revert」
3. Streamlit Cloud 會自動部署舊版本

---

## 效能最佳實踐

✅ **DO**
- 使用 `@st.cache_data` 快取資料
- 使用 `@st.cache_resource` 快取資源
- 限制資料集大小
- 使用資料篩選
- 定期更新依賴

❌ **DON'T**
- 在每次執行時載入大型資料集
- 使用全局變數儲存狀態
- 執行長時間運行的操作
- 使用過多的圖表
- 忽略錯誤處理

---

## 支援

- Streamlit 文件：https://docs.streamlit.io
- Streamlit 社群：https://discuss.streamlit.io
- 反饋：https://help.manus.im

---

## 下一步

1. ✅ 推送代碼到 GitHub
2. ✅ 在 Streamlit Cloud 上部署
3. ✅ 配置 Google Drive 認證
4. ✅ 測試應用程式
5. ✅ 配置自訂域名（可選）
6. ✅ 監控應用程式效能

**祝您部署順利！** 🚀
