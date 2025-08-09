import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from . import config

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SHEET_ID = config.settings.GOOGLE_SHEET_ID
RANGE_NAME = 'offers!A1' # Appends to the 'offers' tab

def get_sheets_service():
    '''Initializes and returns a Google Sheets API service client.'''
    creds = None
    # When running locally, this will use the service account file.
    # When deployed on GCP with a service account, it uses the instance metadata.
    if config.settings.SERVICE_ACCOUNT_FILE and os.path.exists(config.settings.SERVICE_ACCOUNT_FILE):
        creds = service_account.Credentials.from_service_account_file(
            config.settings.SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    else:
        # This path is for when running on GCP with Workload Identity
        from google.auth import default
        creds, _ = default(scopes=SCOPES)
        
    service = build('sheets', 'v4', credentials=creds)
    return service

def append_to_sheet(values: list[list]):
    '''
    Appends rows of data to the configured Google Sheet.
    `values` is a list of lists, where each inner list is a row.
    '''
    try:
        service = get_sheets_service()
        body = {
            'values': values
        }
        result = service.spreadsheets().values().append(
            spreadsheetId=SHEET_ID,
            range=RANGE_NAME,
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        print(f"{result.get('updates').get('updatedCells')} cells appended.")
        return result
    except Exception as e:
        print(f"Error appending to Google Sheet: {e}")
        # Don't fail the whole job if sheets update fails
        return None
