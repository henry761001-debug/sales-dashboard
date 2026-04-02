FROM python:3.11-slim

WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 複製需求檔案
COPY requirements.txt .

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式
COPY . .

# 建立必要的目錄
RUN mkdir -p data temp_uploads temp_exports .streamlit

# 設定 Streamlit 配置
RUN echo "[theme]\nprimaryColor = \"#003366\"\nbackgroundColor = \"#FFFFFF\"\nsecondaryBackgroundColor = \"#F8F9FA\"\ntextColor = \"#2C3E50\"\nfont = \"sans serif\"\n\n[client]\nshowErrorDetails = true\ntoolbarMode = \"viewer\"\n\n[logger]\nlevel = \"info\"\n\n[server]\nheadless = true\nport = 8501\nenableXsrfProtection = true" > .streamlit/config.toml

# 暴露埠
EXPOSE 8501

# 啟動應用程式
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
