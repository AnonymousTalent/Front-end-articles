# 閃電帝國行動 (Lightning Empire Ops) - 工程師手冊

歡迎，帝國的工程師。本手冊將引導您設定、運行並維護這個自動化派單與金流系統。

## 1. 系統概覽

本系統是一個高度模組化的自動化平台，旨在處理來自 Uber/Foodpanda 的訂單，透過加密的核心演算法進行優先級排序與派單，並自動生成金流工單。

### 核心架構
- **`modules/`**: 包含系統的三大功能模組：
    - `dispatch.py`: 派單模組，負責拉取和處理訂單。
    - `payout.py`: 金流模組，負責生成待轉帳的工單。
    - `monitor.py`: 武將調度中心，負責管理和透過 Telegram Bot 發送通知。
- **`core/`**: 存放帝國的核心機密。
    - `core_algo.py`: **加密的**「三距離派單算法」。您只能調用它，無法查看其源碼。
    - `secret.key`: **【極度機密】** 用於解密核心算法的密鑰。**此檔案絕不能提交到任何版本控制系統 (Git)！**
- **`main.py`**: 系統的總控制器和入口點。

## 2. 環境設定 (一鍵部署)

系統的安裝流程已被簡化為一個腳本。

**步驟 1: 執行安裝腳本**
在終端機中，進入專案根目錄 (`lightning_empire_ops/`) 並執行以下指令：
```bash
bash setup.sh
```
此腳本會自動：
1.  建立一個名為 `venv` 的 Python 虛擬環境。
2.  建立 `requirements.txt` 檔案。
3.  安裝所有必要的 Python 函式庫。

**步驟 2: 啟用虛擬環境**
每次要運行或開發此系統前，請務必先啟用虛擬環境：
```bash
source venv/bin/activate
```
當您看到命令提示字元前方出現 `(venv)` 字樣時，表示您已成功進入虛擬環境。

## 3. 系統配置

在運行系統前，您需要配置以下幾項：

**A. Telegram 武將名冊**
- 打開 `data/bot_config.csv` 檔案。
- 根據您負責的模組，填入正確的 Telegram Bot Token。

**B. 派單平台 API Token**
- 打開 `modules/dispatch.py` 檔案。
- 找到 `CONFIG` 字典。
- 將 `ENGINEER_UBER_TOKEN` 和 `ENGINEER_FOODPANDA_TOKEN` 替換為真實的 API Token。

**C. 密鑰檔案 (由總司令提供)**
- 您需要從總司令那裡取得 `secret.key` 檔案。
- 將此檔案放置在 `core/` 目錄下。
- **再次強調：切勿將此檔案上傳到 Git！**

## 4. 運行系統

所有配置完成後，您可以啟動系統。

**正常運行:**
```bash
python main.py
```
系統將會開始主循環，處理訂單並執行所有真實操作。

**安全試運行 (Dry Run):**
強烈建議在修改或測試時使用此模式。它會模擬所有操作，但**不會**執行任何真實的訂單接受或金流工單生成。
```bash
python main.py --dry-run
```

## 5. OpenVPN `noref` 效能優化 (選用)

若您的伺服器環境需要套用 OpenVPN 的 `noref` 補丁以降低 4% 延遲，請遵循以下步驟。

- **環境要求**: Linux 核心版本 4.19+，已啟用 `CONFIG_IPV6` 和 RCU 保護。

- **補丁應用**:
  ```bash
  # 下載補丁
  wget https://lore.kernel.org/netdev/20250912112420.4394-1-mmietus97@yahoo.com/raw -O openvpn-noref.patch

  # 進入您的核心源碼目錄並應用補丁
  # cd /path/to/your/kernel/source
  # git apply openvpn-noref.patch

  # 編譯並安裝模組
  # make -C /path/to/kernel/source M=net/core
  # make -C /path/to/kernel/source M=drivers/net/ovpn
  # sudo make modules_install

  # 重啟 OpenVPN 服務
  # sudo systemctl restart openvpn
  ```

- **效能驗證**:
  使用 `perf` 工具來確認效能提升。
  ```bash
  # perf stat -e cycles,instructions -p $(pidof openvpn)
  ```

---
如有任何問題，請立即向總司令回報。祝您武運昌隆！
