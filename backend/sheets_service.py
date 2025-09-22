from .main import Order
import datetime

# --- Mock Google Sheets Service ---
# This is a placeholder for the actual Google Sheets API integration.
# It simulates logging data by printing to the console.

# In a real application, these would be configured via environment variables
# or a proper config file.
# The user mentioned several spreadsheet names, we would need a mapping here.
SHEET_ID_ORDERS = "YOUR_ORDERS_SPREADSHEET_ID"
SHEET_ID_DISPATCH_LOG = "YOUR_DISPATCH_LOG_SPREADSHEET_ID"

def log_order(order: Order):
    """
    Simulates logging a new order to a Google Sheet.
    """
    timestamp = datetime.datetime.now().isoformat()
    print(f"--- MOCK SHEET LOG ---")
    print(f"Timestamp: {timestamp}")
    print(f"Action: Create Order")
    print(f"Sheet ID: {SHEET_ID_ORDERS}")
    print(f"Data: Order ID={order.id}, Description='{order.description}', Status={order.status}")
    print(f"----------------------")
    # In a real implementation, you would use the Sheets API here:
    # service = build('sheets', 'v4', credentials=creds)
    # values = [[order.id, order.description, order.status, timestamp]]
    # body = {'values': values}
    # result = service.spreadsheets().values().append(
    #     spreadsheetId=SHEET_ID_ORDERS, range='A1',
    #     valueInputOption='RAW', body=body).execute()
    return True

def log_dispatch(order: Order):
    """
    Simulates logging a dispatch event to a Google Sheet.
    """
    timestamp = datetime.datetime.now().isoformat()
    print(f"--- MOCK SHEET LOG ---")
    print(f"Timestamp: {timestamp}")
    print(f"Action: Dispatch Order")
    print(f"Sheet ID: {SHEET_ID_DISPATCH_LOG}")
    print(f"Data: Order ID={order.id}, Assigned to={order.assigned_to}, Status={order.status}")
    print(f"----------------------")
    return True
