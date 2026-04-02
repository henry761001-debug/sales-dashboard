# Google Drive API 設定指南

## 步驟 1：建立 Google Cloud 專案

### 1.1 前往 Google Cloud Console
1. 訪問 [Google Cloud Console](https://console.cloud.google.com/)
2. 登入您的 Google 帳戶
3. 點擊「選擇專案」→「新建專案」

### 1.2 建立新專案
- **專案名稱**：`Sales Dashboard`
- 點擊「建立」

### 1.3 等待專案建立
- 通常需要 1-2 分鐘
- 建立完成後會自動切換到新專案

---

## 步驟 2：啟用 Google Drive API

### 2.1 搜尋 API
1. 在上方搜尋框輸入 `Google Drive API`
2. 點擊搜尋結果中的 `Google Drive API`

### 2.2 啟用 API
1. 點擊「啟用」按鈕
2. 等待 API 啟用完成

---

## 步驟 3：建立 OAuth 2.0 認證

### 3.1 前往認證頁面
1. 左側選單 → 「認證」
2. 點擊「建立認證」→「OAuth 用戶端 ID」

### 3.2 配置 OAuth 同意畫面
如果提示需要設定同意畫面：
1. 點擊「設定同意畫面」
2. 選擇「外部」
3. 填寫應用程式資訊：
   - **應用程式名稱**：`Sales Dashboard`
   - **使用者支援電子郵件**：您的 Gmail 地址
   - **開發者聯絡資訊**：您的 Gmail 地址
4. 點擊「儲存並繼續」
5. 在「範圍」頁面點擊「新增或移除範圍」
6. 搜尋並選擇 `Google Drive API` 的 `../auth/drive.readonly` 範圍
7. 點擊「儲存並繼續」
8. 點擊「回到資訊主頁」

### 3.3 建立 OAuth 用戶端
1. 再次前往「認證」
2. 點擊「建立認證」→「OAuth 用戶端 ID」
3. 應用程式類型選擇「桌面應用程式」
4. 名稱：`Sales Dashboard Desktop`
5. 點擊「建立」

### 3.4 下載認證 JSON
1. 在建立的認證旁點擊下載圖示
2. 將下載的 JSON 檔案命名為 `credentials.json`

---

## 步驟 4：上傳認證檔案到 Streamlit Cloud

### 4.1 在 Streamlit Cloud 中設定 Secrets
1. 前往 [Streamlit Cloud](https://share.streamlit.io/)
2. 登入您的帳戶
3. 選擇您的應用程式
4. 點擊「設定」→「Secrets」
5. 將 `credentials.json` 的內容複製到 Secrets 編輯器

### 4.2 格式化 Secrets
在 Secrets 編輯器中添加：
```toml
[google_drive]
type = "service_account"
project_id = "your_project_id"
private_key_id = "your_private_key_id"
private_key = "your_private_key"
client_email = "your_client_email"
client_id = "your_client_id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your_cert_url"
```

或者直接複製 JSON 內容：
```toml
google_credentials = """
{
  "type": "service_account",
  "project_id": "...",
  ...
}
"""
```

---

## 步驟 5：更新應用程式代碼

### 5.1 修改 google_drive_sync.py
```python
import streamlit as st
import json

# 從 Streamlit Secrets 讀取認證
try:
    if "google_credentials" in st.secrets:
        credentials_json = st.secrets["google_credentials"]
        with open(".google_credentials.json", "w") as f:
            f.write(credentials_json)
except Exception as e:
    st.error(f"Google Drive 認證設定失敗: {str(e)}")
```

### 5.2 在 app.py 中初始化
在應用程式啟動時添加：
```python
from modules import setup_google_credentials
import streamlit as st

# 初始化 Google Drive 認證
if "google_credentials" in st.secrets:
    setup_google_credentials(st.secrets["google_credentials"])
```

---

## 步驟 6：測試 Google Drive 同步

### 6.1 本地測試
1. 建立 `.streamlit/secrets.toml` 檔案
2. 複製您的認證 JSON 內容
3. 執行 `streamlit run app.py`
4. 在側欄選擇「Google Drive 同步」
5. 輸入資料夾 ID：`1fXfFrPuorPb77H95ISjeiKppVFgMlDul`
6. 點擊「同步資料」

### 6.2 Streamlit Cloud 測試
1. 推送代碼到 GitHub
2. 在 Streamlit Cloud 中部署
3. 應用程式應自動使用 Secrets 中的認證
4. 測試 Google Drive 同步功能

---

## 常見問題

### Q: 如何找到 Google Drive 資料夾 ID？
**A**: 
1. 在瀏覽器中打開 Google Drive 資料夾
2. URL 中 `/folders/` 後面的部分就是資料夾 ID
3. 例如：`https://drive.google.com/drive/folders/1fXfFrPuorPb77H95ISjeiKppVFgMlDul`
4. 資料夾 ID 是：`1fXfFrPuorPb77H95ISjeiKppVFgMlDul`

### Q: 認證失敗怎麼辦？
**A**:
1. 檢查 API 是否已啟用
2. 確認認證 JSON 格式正確
3. 驗證 Secrets 中的內容完整
4. 嘗試重新下載認證檔案

### Q: 如何更新認證？
**A**:
1. 在 Google Cloud Console 中刪除舊認證
2. 建立新的 OAuth 用戶端 ID
3. 下載新的 JSON 檔案
4. 更新 Streamlit Cloud 中的 Secrets

### Q: 可以使用服務帳戶嗎？
**A**: 
是的，但需要額外步驟：
1. 在 Google Cloud Console 中建立服務帳戶
2. 下載服務帳戶金鑰
3. 在 Google Drive 中與服務帳戶電子郵件共享資料夾
4. 使用服務帳戶金鑰配置應用程式

---

## 安全性建議

✅ **DO**
- 使用 Streamlit Secrets 儲存認證
- 定期輪換認證
- 限制 API 範圍（唯讀）
- 在 .gitignore 中排除 credentials.json

❌ **DON'T**
- 在代碼中硬編碼認證
- 將認證提交到 Git
- 使用過於寬鬆的權限
- 與他人共享認證檔案

---

## 支援

如有問題，請提交至：https://help.manus.im

**祝您設定順利！** 🚀
