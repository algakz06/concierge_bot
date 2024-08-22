from typing import List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.configs.Settings import settings


class GSRepository():
    creds: Credentials
    GS_SCOPES: List[str]
    GS_SPREADSHEET_ID: str

    def __init__(self):
        self.creds = Credentials.from_authorized_user_file("configs/token.json")
        self.GS_SCOPES = settings.GS_SCOPES
        self.GS_SPREADSHEET_ID = settings.GS_SPREADSHEET_ID

    def get_markup(self):
        ...

    def upload_stats(self):
       ...
