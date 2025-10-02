import datetime
import json
import os

class LedgerEngine:
    """
    帳本引擎 (Ledger Engine)

    負責記錄所有任務的狀態、資金流動與操作歷史。
    這是系統的「單一事實來源 (Single Source of Truth)」。
    所有紀錄都將以 JSON 格式附加到日誌檔案中。
    """
    def __init__(self, log_directory="logs"):
        self.log_directory = os.path.join(os.path.dirname(__file__), '..', log_directory)
        if not os.path.exists(self.log_directory):
            os.makedirs(self.log_directory)

        self.log_file = os.path.join(self.log_directory, "ledger.log")

    def _get_timestamp(self):
        """獲取當前的 ISO 8601 格式時間戳。"""
        return datetime.datetime.now(datetime.timezone.utc).isoformat()

    def record_event(self, event_type, data):
        """
        記錄一個新的事件到帳本中。

        :param event_type: (str) 事件的類型 (e.g., 'TASK_CREATED', 'STATUS_UPDATED', 'TRANSACTION_PROCESSED')
        :param data: (dict) 與事件相關的數據
        """
        log_entry = {
            "timestamp": self._get_timestamp(),
            "event_type": event_type,
            "data": data
        }

        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
            return {"status": "success", "entry": log_entry}
        except IOError as e:
            print(f"Error: Failed to write to ledger log file: {e}")
            return {"status": "error", "message": str(e)}

    def get_all_records(self):
        """
        從帳本中讀取所有紀錄。

        注意：對於大型日誌文件，這可能會消耗大量記憶體。
        在生產環境中，應考慮使用更高效的查詢方法。
        """
        if not os.path.exists(self.log_file):
            return []

        records = []
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    records.append(json.loads(line))
            return records
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error: Failed to read or parse ledger log file: {e}")
            return []

# 範例使用
if __name__ == '__main__':
    ledger = LedgerEngine(log_directory="../../logs/DispatchSystemFoundation")

    # 記錄一個任務創建事件
    task_data = {
        "task_id": "task_12345",
        "description": "Deploy new model to production.",
        "source": "manual_trigger"
    }
    ledger.record_event("TASK_CREATED", task_data)

    # 記錄一個狀態更新事件
    status_update_data = {
        "task_id": "task_12345",
        "old_status": "pending",
        "new_status": "in_progress"
    }
    ledger.record_event("STATUS_UPDATED", status_update_data)

    # 讀取並印出所有紀錄
    all_records = ledger.get_all_records()
    print("All records in ledger:")
    for record in all_records:
        print(json.dumps(record, indent=2, ensure_ascii=False))