import os
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class GoogleSheetsClient:
    """
    A client to interact with Google Sheets.
    """
    def __init__(self, credentials_path=None, sheet_url=None):
        """
        Initializes the client and authenticates with Google Sheets.

        :param credentials_path: Path to the Google Cloud service account JSON file.
        :param sheet_url: URL of the Google Sheet to interact with.
        """
        self.credentials_path = credentials_path or os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH")
        self.sheet_url = sheet_url or os.getenv("GOOGLE_SHEET_URL") # We'll need to add this to .env.example

        if not self.credentials_path:
            raise ValueError("Google Sheets credentials path is not set.")

        self.scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        self.creds = None
        self.client = None
        self.sheet = None

        print("Google Sheets Client initialized.")
        # self.authenticate() # We will call this explicitly when needed

    def authenticate(self):
        """
        Authenticates the client using service account credentials.
        """
        try:
            self.creds = Credentials.from_service_account_file(
                self.credentials_path, scopes=self.scopes
            )
            self.client = gspread.authorize(self.creds)
            print("Successfully authenticated with Google Sheets.")
            return True
        except FileNotFoundError:
            print(f"Error: Credentials file not found at '{self.credentials_path}'.")
            print("Please ensure the path is correct and the file exists.")
            return False
        except Exception as e:
            print(f"An error occurred during authentication: {e}")
            return False

    def open_sheet(self, sheet_url=None):
        """
        Opens a specific Google Sheet by its URL.

        :param sheet_url: The full URL of the Google Sheet.
        """
        target_url = sheet_url or self.sheet_url
        if not target_url:
            print("Error: Google Sheet URL is not provided.")
            return False

        if not self.client:
            print("Authentication must be performed before opening a sheet.")
            if not self.authenticate():
                return False

        try:
            self.sheet = self.client.open_by_url(target_url)
            print(f"Successfully opened sheet: '{self.sheet.title}'")
            return True
        except gspread.exceptions.SpreadsheetNotFound:
            print(f"Error: Spreadsheet not found at URL: {target_url}")
            return False
        except Exception as e:
            print(f"An error occurred while opening the sheet: {e}")
            return False

    def get_worksheet_as_dataframe(self, worksheet_name):
        """
        Retrieves a specific worksheet from the opened sheet as a pandas DataFrame.

        :param worksheet_name: The name of the worksheet (tab).
        :return: A pandas DataFrame or None if an error occurs.
        """
        if not self.sheet:
            print("Error: No sheet is open. Please call open_sheet() first.")
            return None

        try:
            worksheet = self.sheet.worksheet(worksheet_name)
            records = worksheet.get_all_records()
            df = pd.DataFrame(records)
            print(f"Successfully loaded worksheet '{worksheet_name}' into DataFrame.")
            return df
        except gspread.exceptions.WorksheetNotFound:
            print(f"Error: Worksheet '{worksheet_name}' not found in the sheet.")
            return None
        except Exception as e:
            print(f"An error occurred while fetching worksheet '{worksheet_name}': {e}")
            return None

    def append_record(self, worksheet_name, data_dict):
        """
        Appends a new row to a specific worksheet.

        :param worksheet_name: The name of the worksheet (tab).
        :param data_dict: A dictionary representing the row to append.
                          Keys should match the header row of the sheet.
        """
        if not self.sheet:
            print("Error: No sheet is open. Please call open_sheet() first.")
            return

        try:
            worksheet = self.sheet.worksheet(worksheet_name)
            # gspread expects a list of values in the order of the columns
            header = worksheet.row_values(1)
            row_to_append = [data_dict.get(h, "") for h in header]
            worksheet.append_row(row_to_append)
            print(f"Successfully appended record to worksheet '{worksheet_name}'.")
        except gspread.exceptions.WorksheetNotFound:
            print(f"Error: Worksheet '{worksheet_name}' not found in the sheet.")
        except Exception as e:
            print(f"An error occurred while appending to '{worksheet_name}': {e}")

if __name__ == '__main__':
    print("This is a client module for Google Sheets interaction.")
    print("Example Usage:")
    print("1. Set GOOGLE_SHEETS_CREDENTIALS_PATH and GOOGLE_SHEET_URL in your .env file.")
    print("2. from google_sheets_client import GoogleSheetsClient")
    print("3. client = GoogleSheetsClient()")
    print("4. if client.open_sheet():")
    print("5.    df = client.get_worksheet_as_dataframe('Sheet1')")
    print("6.    if df is not None: print(df.head())")
