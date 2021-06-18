import re

from googleapiclient.discovery import build
from google.oauth2 import service_account


SCOPES = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive']

SERVICE_ACCOUNT_FILE = 'credentials.json'


def parse(url: str):
    pattern = 'https://docs.google.com/spreadsheets/d/\w+/edit#gid=\d+'
    if re.match(pattern, url):
        table, sheet = url.split('https://docs.google.com/spreadsheets/d/')[1].split('/edit#gid=')
        return table, sheet


def insert(spreadsheet_id,
           sheet_id='0',
           values: list = [[]],
           sample_range: str = 'A:AG'):
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build('sheets', 'v4', credentials=creds)
    body = {
        'values': values,
        "majorDimension": "ROWS",
    }

    # Call the Sheets API
    try:
        sheet = service.spreadsheets()
        sheets = sheet.get(spreadsheetId=spreadsheet_id).execute().get('sheets')
        sheet_title = [sheet for sheet in sheets if str(sheet['properties']['sheetId']) == sheet_id][0]['properties']['title']

        service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id, range=f"{sheet_title}!{sample_range}",
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body=body).execute()
    except Exception as error:
        return False
    return True
