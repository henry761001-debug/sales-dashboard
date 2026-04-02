"""
Google Drive 同步模組
支援三種認證方式：
1. Streamlit Secrets（服務帳戶 JSON）
2. 本地服務帳戶 JSON 檔案
3. OAuth 2.0 本地流程（僅開發環境）
"""

import os
import io
import json
import tempfile
from typing import Tuple, List, Optional

# 嘗試導入 Google 套件
try:
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False

try:
    from google.oauth2 import service_account
    from google.auth.transport.requests import Request
    GOOGLE_AUTH_AVAILABLE = True
except ImportError:
    GOOGLE_AUTH_AVAILABLE = False

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    OAUTH_AVAILABLE = True
except ImportError:
    OAUTH_AVAILABLE = False

# Google Drive API 設定
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
LOCAL_CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), '..', '.google_credentials.json')
LOCAL_TOKEN_FILE = os.path.join(os.path.dirname(__file__), '..', '.google_drive_token.pickle')


def _get_service_from_streamlit_secrets():
    """從 Streamlit Secrets 建立 Google Drive 服務"""
    try:
        import streamlit as st
        if "google_credentials" not in st.secrets:
            return None, "Streamlit Secrets 中未找到 google_credentials"
        
        credentials_content = st.secrets["google_credentials"]
        
        # 解析 JSON
        if isinstance(credentials_content, str):
            creds_dict = json.loads(credentials_content)
        else:
            creds_dict = dict(credentials_content)
        
        # 建立服務帳戶憑證
        creds = service_account.Credentials.from_service_account_info(
            creds_dict, scopes=SCOPES
        )
        
        service = build('drive', 'v3', credentials=creds)
        return service, None
    
    except Exception as e:
        return None, f"從 Streamlit Secrets 建立服務失敗: {str(e)}"


def _get_service_from_local_service_account():
    """從本地服務帳戶 JSON 建立 Google Drive 服務"""
    try:
        if not os.path.exists(LOCAL_CREDENTIALS_FILE):
            return None, "本地認證檔案不存在"
        
        with open(LOCAL_CREDENTIALS_FILE, 'r') as f:
            creds_dict = json.load(f)
        
        # 檢查是否為服務帳戶類型
        if creds_dict.get('type') == 'service_account':
            creds = service_account.Credentials.from_service_account_info(
                creds_dict, scopes=SCOPES
            )
            service = build('drive', 'v3', credentials=creds)
            return service, None
        else:
            return None, "本地認證不是服務帳戶類型，請使用 OAuth 流程"
    
    except Exception as e:
        return None, f"從本地服務帳戶建立服務失敗: {str(e)}"


def _get_service_from_oauth():
    """使用 OAuth 2.0 建立 Google Drive 服務（僅開發環境）"""
    try:
        import pickle
        
        if not OAUTH_AVAILABLE:
            return None, "OAuth 套件未安裝"
        
        creds = None
        
        # 讀取已保存的 token
        if os.path.exists(LOCAL_TOKEN_FILE):
            with open(LOCAL_TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)
        
        # 更新過期的 token
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(LOCAL_TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)
        
        if creds and creds.valid:
            service = build('drive', 'v3', credentials=creds)
            return service, None
        
        # 需要重新認證
        if not os.path.exists(LOCAL_CREDENTIALS_FILE):
            return None, "OAuth 認證檔案不存在"
        
        flow = InstalledAppFlow.from_client_secrets_file(LOCAL_CREDENTIALS_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
        
        with open(LOCAL_TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
        
        service = build('drive', 'v3', credentials=creds)
        return service, None
    
    except Exception as e:
        return None, f"OAuth 認證失敗: {str(e)}"


class GoogleDriveSync:
    """
    Google Drive 同步器
    自動偵測並使用最適合的認證方式
    """
    
    def __init__(self):
        self.service = None
        self.auth_method = None
        self.auth_error = None
        self._authenticate()
    
    def _authenticate(self):
        """自動偵測並使用最適合的認證方式"""
        if not GOOGLE_API_AVAILABLE or not GOOGLE_AUTH_AVAILABLE:
            self.auth_error = "Google API 套件未安裝，請執行：pip install google-api-python-client google-auth"
            return
        
        # 方法 1：嘗試 Streamlit Secrets（服務帳戶）
        service, error = _get_service_from_streamlit_secrets()
        if service:
            self.service = service
            self.auth_method = "streamlit_secrets"
            return
        
        # 方法 2：嘗試本地服務帳戶 JSON
        service, error = _get_service_from_local_service_account()
        if service:
            self.service = service
            self.auth_method = "local_service_account"
            return
        
        # 方法 3：嘗試 OAuth（僅開發環境）
        service, error = _get_service_from_oauth()
        if service:
            self.service = service
            self.auth_method = "oauth"
            return
        
        self.auth_error = (
            "Google Drive 認證失敗。請選擇以下其中一種方式設定：\n\n"
            "**方式 A（推薦）：服務帳戶**\n"
            "1. 前往 Google Cloud Console → 建立服務帳戶\n"
            "2. 下載 JSON 金鑰\n"
            "3. 在 Google Drive 資料夾中共享給服務帳戶電子郵件\n"
            "4. 將 JSON 內容設定到 Streamlit Secrets 的 `google_credentials`\n\n"
            "**方式 B：本地 OAuth（開發環境）**\n"
            "1. 下載 OAuth 2.0 認證 JSON\n"
            "2. 儲存為 `.google_credentials.json`\n"
            "3. 重新啟動應用程式"
        )
    
    @property
    def is_authenticated(self) -> bool:
        return self.service is not None
    
    def find_file_in_folder(self, folder_id: str, file_name: str) -> Optional[str]:
        """在指定資料夾中查找檔案，返回檔案 ID"""
        if not self.service:
            return None
        try:
            query = f"'{folder_id}' in parents and name='{file_name}' and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)',
                pageSize=1
            ).execute()
            files = results.get('files', [])
            return files[0]['id'] if files else None
        except Exception as e:
            return None
    
    def download_file(self, file_id: str, file_name: str) -> Tuple[bool, Optional[bytes], str]:
        """下載 Google Drive 檔案，返回 (成功, 內容, 錯誤訊息)"""
        if not self.service:
            return False, None, "未認證"
        try:
            request = self.service.files().get_media(fileId=file_id)
            buffer = io.BytesIO()
            downloader = MediaIoBaseDownload(buffer, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()
            return True, buffer.getvalue(), ""
        except Exception as e:
            return False, None, f"下載 {file_name} 失敗: {str(e)}"
    
    def sync_files(
        self,
        folder_id: str,
        file_names: List[str],
        save_dir: str
    ) -> Tuple[bool, List[str], List[str]]:
        """
        同步多個檔案到本地目錄
        返回 (全部成功, 成功檔案清單, 錯誤清單)
        """
        if not self.service:
            return False, [], [self.auth_error or "Google Drive 未認證"]
        
        os.makedirs(save_dir, exist_ok=True)
        success_files = []
        errors = []
        
        for file_name in file_names:
            file_id = self.find_file_in_folder(folder_id, file_name)
            if not file_id:
                errors.append(f"❌ 找不到檔案：{file_name}（請確認資料夾中有此檔案且名稱完全相符）")
                continue
            
            success, content, error_msg = self.download_file(file_id, file_name)
            if not success:
                errors.append(error_msg)
                continue
            
            try:
                file_path = os.path.join(save_dir, file_name)
                with open(file_path, 'wb') as f:
                    f.write(content)
                success_files.append(file_name)
            except Exception as e:
                errors.append(f"保存 {file_name} 失敗: {str(e)}")
        
        return len(errors) == 0, success_files, errors
    
    def get_folder_contents(self, folder_id: str) -> Tuple[bool, List[dict], str]:
        """獲取資料夾內容清單"""
        if not self.service:
            return False, [], self.auth_error or "未認證"
        try:
            query = f"'{folder_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, mimeType, modifiedTime)',
                pageSize=100
            ).execute()
            files = results.get('files', [])
            return True, files, ""
        except Exception as e:
            return False, [], f"獲取資料夾內容失敗: {str(e)}"


def setup_google_credentials(credentials_json: str) -> bool:
    """
    設置本地 Google 認證檔案
    credentials_json: 認證 JSON 字串
    """
    try:
        creds_path = os.path.abspath(LOCAL_CREDENTIALS_FILE)
        with open(creds_path, 'w') as f:
            f.write(credentials_json)
        return True
    except Exception as e:
        print(f"設置認證檔案失敗: {str(e)}")
        return False


def clear_google_token():
    """清除已保存的 Google Drive token"""
    try:
        if os.path.exists(LOCAL_TOKEN_FILE):
            os.remove(LOCAL_TOKEN_FILE)
        return True
    except Exception as e:
        print(f"清除 token 失敗: {str(e)}")
        return False
