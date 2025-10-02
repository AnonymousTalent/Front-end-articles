import unittest
import os
import json
import sys
import shutil

# 將專案根目錄添加到 sys.path，以便導入 `scripts` 模組
# This allows running the test directly, e.g., `python3 tests/test_ledger_engine.py`
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.ledger_engine import LedgerEngine

class TestLedgerEngine(unittest.TestCase):
    """
    針對 LedgerEngine 類別的單元測試。
    """
    def setUp(self):
        """在每個測試開始前，設置一個臨時的日誌目錄和 LedgerEngine 實例。"""
        self.test_log_dir = os.path.join(os.path.dirname(__file__), "temp_test_logs")
        # 確保測試目錄是全新的
        if os.path.exists(self.test_log_dir):
            shutil.rmtree(self.test_log_dir)

        self.ledger = LedgerEngine(log_directory=self.test_log_dir)
        self.log_file_path = self.ledger.log_file

    def tearDown(self):
        """在每個測試結束後，清理臨時的日誌文件和目錄。"""
        if os.path.exists(self.test_log_dir):
            shutil.rmtree(self.test_log_dir)

    def test_01_log_directory_creation(self):
        """測試：日誌目錄是否在初始化時被成功創建。"""
        self.assertTrue(os.path.exists(self.ledger.log_directory), "日誌目錄應該被創建")

    def test_02_record_single_event(self):
        """測試：能否成功記錄一個單一事件到帳本中。"""
        event_type = "TEST_EVENT"
        data = {"test_key": "test_value", "id": 1}

        result = self.ledger.record_event(event_type, data)

        # 驗證返回結果
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['entry']['event_type'], event_type)
        self.assertEqual(result['entry']['data'], data)

        # 驗證文件內容
        self.assertTrue(os.path.exists(self.log_file_path), "日誌文件應該被創建")
        with open(self.log_file_path, 'r', encoding='utf-8') as f:
            line = f.readline()
            record = json.loads(line)
            self.assertEqual(record['event_type'], event_type)
            self.assertEqual(record['data'], data)

    def test_03_get_all_records(self):
        """測試：能否從帳本中讀取所有記錄。"""
        event1_data = {"event_id": 1, "message": "First event"}
        event2_data = {"event_id": 2, "message": "Second event"}

        self.ledger.record_event("EVENT_1", event1_data)
        self.ledger.record_event("EVENT_2", event2_data)

        records = self.ledger.get_all_records()

        self.assertEqual(len(records), 2, "應該有兩條記錄")
        self.assertEqual(records[0]['event_type'], "EVENT_1")
        self.assertEqual(records[0]['data'], event1_data)
        self.assertEqual(records[1]['event_type'], "EVENT_2")
        self.assertEqual(records[1]['data'], event2_data)

    def test_04_get_records_from_empty_ledger(self):
        """測試：當日誌文件不存在時，讀取記錄應返回一個空列表。"""
        # 在 setUp 中，日誌文件是空的，所以直接讀取即可
        records = self.ledger.get_all_records()
        self.assertEqual(records, [], "從空的帳本中讀取應返回空列表")

if __name__ == '__main__':
    unittest.main(verbosity=2)