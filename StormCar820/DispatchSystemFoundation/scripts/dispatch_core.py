import uuid
from .ledger_engine import LedgerEngine

class DispatchCore:
    """
    派單系統核心 (Dispatch System Core)

    後端系統的大腦，負責接收、解析、指派和追蹤任務。
    它與 LedgerEngine 緊密互動，以確保所有操作都被忠實記錄。
    """
    def __init__(self, ledger_engine: LedgerEngine):
        self.ledger_engine = ledger_engine
        self.tasks = self._load_tasks_from_ledger()

    def _load_tasks_from_ledger(self):
        """從帳本歷史中重建當前的任務狀態。"""
        tasks = {}
        records = self.ledger_engine.get_all_records()
        for record in records:
            if record['event_type'] == 'TASK_CREATED':
                task_id = record['data']['task_id']
                tasks[task_id] = record['data']
                tasks[task_id]['status'] = 'created' # 初始狀態
            elif record['event_type'] == 'STATUS_UPDATED':
                task_id = record['data']['task_id']
                if task_id in tasks:
                    tasks[task_id]['status'] = record['data']['new_status']
        return tasks

    def create_task(self, description, source="unknown"):
        """
        創建一個新任務。

        :param description: (str) 任務的詳細描述。
        :param source: (str) 任務來源 (e.g., 'api', 'telegram_bot')。
        :return: (dict) 包含新任務 ID 和數據的字典。
        """
        task_id = str(uuid.uuid4())
        task_data = {
            "task_id": task_id,
            "description": description,
            "source": source,
            "status": "pending",
        }

        # 透過帳本引擎記錄事件
        self.ledger_engine.record_event("TASK_CREATED", task_data)

        # 更新內存中的任務狀態
        self.tasks[task_id] = task_data

        print(f"Task {task_id} created.")
        return task_data

    def update_task_status(self, task_id, new_status):
        """
        更新現有任務的狀態。

        :param task_id: (str) 要更新的任務 ID。
        :param new_status: (str) 新的狀態 (e.g., 'assigned', 'in_progress', 'completed', 'failed')。
        :return: (dict) 成功或失敗的訊息。
        """
        if task_id not in self.tasks:
            return {"status": "error", "message": "Task not found."}

        old_status = self.tasks[task_id].get('status', 'unknown')

        status_update_data = {
            "task_id": task_id,
            "old_status": old_status,
            "new_status": new_status
        }

        # 透過帳本引擎記錄事件
        self.ledger_engine.record_event("STATUS_UPDATED", status_update_data)

        # 更新內存中的任務狀態
        self.tasks[task_id]['status'] = new_status

        print(f"Task {task_id} status updated to {new_status}.")
        return {"status": "success", "data": self.tasks[task_id]}

    def get_task(self, task_id):
        """獲取特定任務的詳細資訊。"""
        return self.tasks.get(task_id, None)

# 範例使用
if __name__ == '__main__':
    # 初始化帳本引擎
    ledger = LedgerEngine(log_directory="../../logs/DispatchSystemFoundation")

    # 初始化派單核心
    dispatcher = DispatchCore(ledger)

    # 創建一個新任務
    new_task = dispatcher.create_task(
        description="Refactor the authentication module.",
        source="api_request"
    )
    task_id = new_task['task_id']
    print(f"New task created: {new_task}")

    # 更新任務狀態
    dispatcher.update_task_status(task_id, "in_progress")

    # 再次更新任務狀態
    dispatcher.update_task_status(task_id, "completed")

    # 獲取任務資訊
    final_task_state = dispatcher.get_task(task_id)
    print(f"Final task state: {final_task_state}")

    # 驗證帳本記錄
    print("\n--- Ledger Records ---")
    all_records = ledger.get_all_records()
    import json
    for record in all_records:
        print(json.dumps(record, indent=2, ensure_ascii=False))