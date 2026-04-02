# 部署與維護指南

## 本地部署

### 系統要求
- Python 3.11+
- 4GB RAM 最小
- 100MB 磁碟空間

### 安裝步驟

1. **克隆或下載專案**
```bash
cd /home/ubuntu/sales_dashboard
```

2. **建立虛擬環境（可選但建議）**
```bash
python3.11 -m venv venv
source venv/bin/activate
```

3. **安裝依賴**
```bash
pip3 install -r requirements.txt
```

4. **生成測試資料**
```bash
python3.11 generate_sample_data.py
```

5. **啟動應用程式**
```bash
streamlit run app.py
```

---

## Docker 部署

### 構建 Docker 映像
```bash
docker build -t sales-dashboard:latest .
```

### 執行 Docker 容器
```bash
docker run -p 8501:8501 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/temp_exports:/app/temp_exports \
  -e OPENAI_API_KEY=your_key \
  sales-dashboard:latest
```

### Docker Compose（可選）
```yaml
version: '3.8'

services:
  dashboard:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
      - ./temp_exports:/app/temp_exports
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    restart: unless-stopped
```

執行：
```bash
docker-compose up -d
```

---

## 雲端部署

### Streamlit Cloud

1. **推送到 GitHub**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/your-repo/sales-dashboard.git
git push -u origin main
```

2. **連接到 Streamlit Cloud**
- 前往 https://share.streamlit.io
- 登入 GitHub 帳戶
- 選擇「New app」
- 選擇倉庫、分支和檔案路徑

3. **設定環境變數**
- 在 Streamlit Cloud 儀表板中設定 `OPENAI_API_KEY`

### Heroku 部署

1. **建立 Procfile**
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

2. **建立 runtime.txt**
```
python-3.11.0
```

3. **部署**
```bash
heroku login
heroku create your-app-name
git push heroku main
```

### AWS EC2 部署

1. **啟動 EC2 實例**
- 選擇 Ubuntu 22.04 LTS
- 開放埠 8501

2. **SSH 連接並安裝**
```bash
ssh -i your-key.pem ubuntu@your-instance-ip
sudo apt-get update
sudo apt-get install python3.11 python3-pip
cd /home/ubuntu
git clone your-repo
cd sales-dashboard
pip3 install -r requirements.txt
```

3. **使用 systemd 作為服務**
```bash
sudo nano /etc/systemd/system/streamlit.service
```

內容：
```ini
[Unit]
Description=Streamlit Dashboard
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/sales_dashboard
ExecStart=/usr/bin/python3.11 -m streamlit run app.py --server.port=8501 --server.address=0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

啟動服務：
```bash
sudo systemctl daemon-reload
sudo systemctl enable streamlit
sudo systemctl start streamlit
```

---

## 配置管理

### 環境變數

建立 `.env` 檔案：
```
OPENAI_API_KEY=your_openai_key
GOOGLE_DRIVE_FOLDER_ID=1fXfFrPuorPb77H95ISjeiKppVFgMlDul
DEBUG=false
```

### Streamlit 配置

編輯 `.streamlit/config.toml`：
```toml
[theme]
primaryColor = "#003366"
backgroundColor = "#FFFFFF"

[server]
port = 8501
headless = true
enableXsrfProtection = true
maxUploadSize = 200

[client]
showErrorDetails = true
```

---

## 監控與日誌

### 檢查應用程式狀態
```bash
ps aux | grep streamlit
```

### 查看日誌
```bash
tail -f /tmp/streamlit.log
```

### 性能監控
```bash
# CPU 和記憶體使用
top -p $(pgrep -f streamlit)

# 磁碟使用
du -sh /home/ubuntu/sales_dashboard
```

---

## 備份與恢復

### 備份資料
```bash
# 備份所有資料檔案
tar -czf sales_dashboard_backup_$(date +%Y%m%d).tar.gz data/

# 上傳到 S3（可選）
aws s3 cp sales_dashboard_backup_*.tar.gz s3://your-bucket/backups/
```

### 恢復資料
```bash
tar -xzf sales_dashboard_backup_20260403.tar.gz
```

---

## 更新與升級

### 更新應用程式
```bash
git pull origin main
pip3 install --upgrade -r requirements.txt
systemctl restart streamlit
```

### 更新依賴
```bash
pip3 list --outdated
pip3 install --upgrade package_name
```

---

## 安全性最佳實踐

### 1. API 金鑰管理
- 永遠不要在代碼中提交 API 金鑰
- 使用環境變數或密鑰管理服務
- 定期輪換金鑰

### 2. 資料保護
- 使用 HTTPS（在生產環境）
- 加密敏感資料
- 定期備份

### 3. 存取控制
- 使用 Streamlit 的認證機制
- 限制 IP 存取
- 使用防火牆規則

### 4. 日誌與監控
- 啟用詳細日誌
- 監控異常活動
- 定期審計日誌

---

## 故障排除

### 應用程式崩潰
```bash
# 檢查日誌
tail -100 /tmp/streamlit.log

# 重啟服務
systemctl restart streamlit

# 檢查資源使用
free -h
df -h
```

### 高記憶體使用
- 減少快取大小
- 限制資料集大小
- 優化圖表生成

### 連接超時
- 檢查網路連線
- 增加超時設定
- 檢查防火牆規則

---

## 效能優化

### 1. 快取優化
```python
@st.cache_data
def load_data():
    # 載入資料
    pass
```

### 2. 資料庫優化
- 使用索引
- 定期清理舊資料
- 分區大型表

### 3. 圖表優化
- 限制資料點數
- 使用聚合資料
- 異步生成

---

## 支援與反饋

- 文件：https://docs.streamlit.io
- 社群：https://discuss.streamlit.io
- 反饋：https://help.manus.im

---

## 版本歷史

| 版本 | 日期 | 變更 |
|------|------|------|
| 1.0 | 2026-04-03 | 初始發佈 |

---

**最後更新**：2026-04-03

祝您部署順利！ 🚀
