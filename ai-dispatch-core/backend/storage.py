import pandas as pd
from datetime import datetime

def record_dispatch(order, rider, success=True):
    """
    將派單結果記錄到儲存系統（例如 CSV, Google Sheets, DB）。

    在此模擬中，我們將結果打印出來，並可以選擇性地存到一個新的 CSV 中。
    """
    record = {
        "timestamp": datetime.now().isoformat(),
        "order_id": order['id'],
        "assigned_rider_id": rider['id'],
        "assigned_rider_name": rider['name'],
        "success": success,
        "order_details": order.to_dict(),
        "rider_details": rider.to_dict()
    }

    print("--- 儲存系統 ---")
    print("記錄一筆新的派單結果：")
    print(record)
    print("------------------")

    # 也可以附加到一個日誌檔案
    # with open("data/dispatch_log.csv", "a") as f:
    #     f.write(f"{record['timestamp']},{record['order_id']},{record['assigned_rider_id']}\n")

    return True

if __name__ == '__main__':
    mock_order = pd.Series({'id': 'C789', 'value': 150})
    mock_rider = pd.Series({'id': 'R08', 'name': '急先鋒'})

    print("測試記錄功能：")
    record_dispatch(mock_order, mock_rider)
