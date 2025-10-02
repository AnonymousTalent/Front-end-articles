import time
from scripts.ledger_engine import LedgerEngine
from scripts.dispatch_core import DispatchCore
from scripts.ai_module import AIModule
from scripts.finance_engine import FinanceEngine

class RadarStationApplication:
    """
    雷達站主應用程式 (Radar Station Main Application)

    負責初始化並協調所有核心模組，形成一個可運行的系統。
    """
    def __init__(self):
        print("--- Radar Station System Initializing ---")
        # 1. 初始化日誌與資料庫引擎
        self.ledger = LedgerEngine(log_directory="../logs/DispatchSystemFoundation")

        # 2. 初始化核心業務模組
        self.dispatcher = DispatchCore(self.ledger)
        self.ai_module = AIModule()
        self.finance_engine = FinanceEngine() # 實際應用中可能需要傳入資料庫連線

        print("--- All Core Modules Initialized Successfully ---\n")

    def run_simulation(self):
        """
        運行一個模擬場景，展示完整的端到端工作流程。
        """
        print("--- Starting End-to-End Simulation ---")

        # === 步驟 1: 創建一個新任務 ===
        print("\n[Step 1] Creating a new task...")
        task_description = "Generate a market analysis report for Q4."
        new_task = self.dispatcher.create_task(description=task_description, source="simulation")
        task_id = new_task['task_id']
        print(f"Task '{task_id}' created.")

        # === 步驟 2: AI 模組處理任務 ===
        print(f"\n[Step 2] AI Module processing task '{task_id}'...")
        self.dispatcher.update_task_status(task_id, "ai_processing")
        # 2a. 使用 Gemini (mock) 生成內容
        generated_content = self.ai_module.generate_content(prompt=task_description)
        print("AI has generated the content.")
        # 2b. 使用 Grok4 (mock) 審核內容
        review_result = self.ai_module.review_and_verify(generated_content['content'])
        print(f"AI has reviewed the content. Result: {review_result['result']}")

        if review_result['result'] != 'approved':
            self.dispatcher.update_task_status(task_id, "failed_review")
            print("--- Simulation Ended: Task failed AI review. ---")
            return

        self.dispatcher.update_task_status(task_id, "review_approved")

        # === 步驟 3: 金流引擎處理交易 ===
        print(f"\n[Step 3] Finance Engine processing transaction for task '{task_id}'...")
        transaction_data = {
            "order_id": task_id,
            "amount": 150.00, # 假設的任務價值
            "currency": "USD",
            "description": task_description
        }
        self.finance_engine.process_transaction(transaction_data)

        # === 步驟 4: 完成任務 ===
        print(f"\n[Step 4] Finalizing task '{task_id}'...")
        self.dispatcher.update_task_status(task_id, "completed")

        print("\n--- Simulation Completed Successfully ---")

        # === 驗證: 顯示帳本中的所有紀錄 ===
        print("\n--- Final Ledger State ---")
        all_records = self.ledger.get_all_records()
        import json
        for record in all_records:
            print(json.dumps(record, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    app = RadarStationApplication()
    app.run_simulation()
    print("\n--- Radar Station Application has finished its run. ---")