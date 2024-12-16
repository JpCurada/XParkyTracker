from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd
from typing import Optional, List, Dict
from streamlit.runtime.state.session_state import AttrDict

class GoogleAPIClient:
    """Client for accessing Google Drive and Sheets APIs."""
    
    def __init__(self, credentials_dict: AttrDict):
        """Initialize Google API client with service account credentials."""
        self.SCOPES = [
            'https://www.googleapis.com/auth/drive.readonly',
            'https://www.googleapis.com/auth/spreadsheets.readonly'
        ]
        
        # Convert AttrDict to regular dict and create credentials object
        credentials_info = dict(credentials_dict)
        self.credentials = service_account.Credentials.from_service_account_info(
            credentials_info,
            scopes=self.SCOPES
        )
        
        # Initialize services with the credentials
        self.drive_service = build('drive', 'v3', credentials=self.credentials)
        self.sheets_service = build('sheets', 'v4', credentials=self.credentials)
        
    def list_files_in_folder(self, folder_id: str) -> List[Dict]:
        """List all files in a specific Google Drive folder."""
        try:
            results = self.drive_service.files().list(
                q=f"'{folder_id}' in parents",
                fields="files(id, name)"
            ).execute()
            return results.get('files', [])
        except Exception as e:
            print(f"Error listing files: {str(e)}")
            return []

    def get_sheet_data(self, spreadsheet_id: str, sheet_name: str) -> Optional[pd.DataFrame]:
        """Retrieve data from a Google Sheet as a pandas DataFrame."""
        try:
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=f"{sheet_name}!A1:Z"
            ).execute()
            
            values = result.get('values', [])
            if not values:
                return None
                
            df = pd.DataFrame(values[1:], columns=values[0])
            return df
            
        except Exception as e:
            print(f"Error getting sheet data: {str(e)}")
            return None
