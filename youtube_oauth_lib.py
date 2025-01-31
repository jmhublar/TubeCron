# youtube_oauth_lib.py
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

class YouTubeAuth:
    def __init__(self, credentials_path, token_path):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.creds = None

    def authenticate(self):
        if os.path.exists(self.token_path):
            self.creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, SCOPES)
            self.creds = flow.run_local_server(port=8080)
            self.save_token()
        
        if not self.creds or not self.creds.valid:
            raise Exception("Failed to obtain valid credentials")

        return self.creds

    def save_token(self):
        with open(self.token_path, 'w') as f:
            f.write(self.creds.to_json())

    def get_authenticated_service(self):
        from googleapiclient.discovery import build
        if not self.creds:
            self.authenticate()
        return build("youtube", "v3", credentials=self.creds)
