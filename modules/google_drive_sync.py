"""
Google Drive 同步模組
負責從 Google Drive 下載指定檔案
"""

import os
import io
from typing import Tuple, List, Optional
import pickle

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google.auth.oauthlib.flow import InstalledAppFlow
    from google.api_python_client import discovery
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

# Google Drive API 設定
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
TOKEN_FILE = '/home/ubuntu/sales_dashboard/.google_drive_token.pickle'
CREDENTIALS_FILE = '/home/ubuntu/sales_dashboard/.google_credentials.json'


class GoogleDriveSync:
    """Google Drive 同步器"""
    
    def __init__(self):
        self.service = None
        self.authenticate()
    
    def authenticate(self) -> bool:
        """
        認證 Google Drive API
        """
        if not GOOGLE_AVAILABLE:
            print("Google Auth 套件未安裝")
            return False
        
        try:
            creds = None
            
            # 檢查是否有已保存的 token
            if os.path.exists(TOKEN_FILE):
                with open(TOKEN_FILE, 'rb') as token:
                    creds = pickle.load(token)
            
            # 如果沒有有效的 credentials，進行 OAuth 流程
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not os.path.exists(CREDENTIALS_FILE):
                        return False
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        CREDENTIALS_FILE, SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # 保存 token 供下次使用
                with open(TOKEN_FILE, 'wb') as token:
                    pickle.dump(creds, token)
            
            self.service = discovery.build('drive', 'v3', credentials=creds)
            return True
        
        except Exception as e:
            print(f"Google Drive 認證失敗: {str(e)}")
            return False
    
    def find_file_in_folder(
        self,
        folder_id: str,
        file_name: str
    ) -> Optional[str]:
        """
        在指定資料夾中查找檔案
        返回檔案 ID，如果找不到則返回 None
        """
        try:
            query = f"'{folder_id}' in parents and name='{file_name}' and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)',
                pageSize=1
            ).execute()
            
            files = results.get('files', [])
            if files:
                return files[0]['id']
            return None
        
        except Exception as e:
            print(f"查找檔案失敗: {str(e)}")
            return None
    
    def download_file(
        self,
        file_id: str,
        file_name: str
    ) -> Tuple[bool, Optional[bytes], str]:
        """
        下載 Google Drive 檔案
        返回 (成功, 檔案內容, 錯誤訊息)
        """
        try:
            request = self.service.files().get_media(fileId=file_id)
            file_content = request.execute()
            return True, file_content, ""
        
        except Exception as e:
            error_msg = f"下載 {file_name} 失敗: {str(e)}"
            return False, None, error_msg
    
    def sync_files(
        self,
        folder_id: str,
        file_names: List[str],
        save_dir: str
    ) -> Tuple[bool, List[str], List[str]]:
        """
        同步多個檔案
        返回 (全部成功, 成功檔案清單, 錯誤清單)
        """
        if not self.service:
            return False, [], ["Google Drive 未認證"]
        
        success_files = []
        errors = []
        
        for file_name in file_names:
            # 查找檔案
            file_id = self.find_file_in_folder(folder_id, file_name)
            
            if not file_id:
                errors.append(f"找不到檔案: {file_name}")
                continue
            
            # 下載檔案
            success, content, error_msg = self.download_file(file_id, file_name)
            
            if not success:
                errors.append(error_msg)
                continue
            
            # 保存檔案
            try:
                file_path = os.path.join(save_dir, file_name)
                with open(file_path, 'wb') as f:
                    f.write(content)
                success_files.append(file_name)
            except Exception as e:
                errors.append(f"保存 {file_name} 失敗: {str(e)}")
        
        return len(errors) == 0, success_files, errors
    
    def get_folder_contents(self, folder_id: str) -> Tuple[bool, List[dict], str]:
        """
        獲取資料夾內容
        返回 (成功, 檔案清單, 錯誤訊息)
        """
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
            error_msg = f"獲取資料夾內容失敗: {str(e)}"
            return False, [], error_msg


def setup_google_credentials(credentials_json: str) -> bool:
    """
    設置 Google 認證檔案
    credentials_json: 認證 JSON 內容
    """
    try:
        with open(CREDENTIALS_FILE, 'w') as f:
            f.write(credentials_json)
        return True
    except Exception as e:
        print(f"設置認證檔案失敗: {str(e)}")
        return False


def clear_google_token():
    """清除已保存的 Google Drive token"""
    try:
        if os.path.exists(TOKEN_FILE):
            os.remove(TOKEN_FILE)
        return True
    except Exception as e:
        print(f"清除 token 失敗: {str(e)}")
        return False
