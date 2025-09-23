# -*- coding: utf-8 -*-

"""
Central configuration file for the Flash Dispatch system.
NOTE: In a real production environment, sensitive data should be loaded from
environment variables or a secure vault, not hardcoded in a file.
This file is included in .gitignore to prevent accidental commits of secrets.
"""

from cryptography.fernet import Fernet
import os

def get_secret(name, default=None):
    """Retrieves a secret from environment variables."""
    value = os.getenv(name)
    if value:
        return value
    if default is not None:
        print(f"Warning: Environment variable {name} not set. Using default placeholder.")
        return default
    raise ValueError(f"Critical Error: Environment variable {name} is not set and no default is provided.")

# --- SENSITIVE DATA ---
# All sensitive data is loaded from environment variables.
TELEGRAM_TOKEN = get_secret("TELEGRAM_TOKEN")
LINE_NOTIFY_TOKEN = get_secret("LINE_NOTIFY_TOKEN", "YOUR_LINE_NOTIFY_TOKEN_HERE")
API_SECRET = get_secret("API_SECRET", "YOUR_API_SECRET_FOR_SIGNATURES")
UBER_TOKEN = get_secret("UBER_TOKEN", "YOUR_UBER_API_TOKEN_HERE")
FOODPANDA_TOKEN = get_secret("FOODPANDA_TOKEN", "YOUR_FOODPANDA_API_TOKEN_HERE")

# --- BANKING INFORMATION (Corrected to Chunghwa Post as per latest instruction) ---
BANK_SWIFT_CODE = "CHPYTWTP"
BANK_ACCOUNT = get_secret("BANK_ACCOUNT", "00210091602429")
BANK_ACCOUNT_NAME = get_secret("BANK_ACCOUNT_NAME", "Chiclin Hus")
BANK_NAME = "Chunghwa Post Co., Ltd."
BANK_ADDRESS = get_secret("BANK_ADDRESS", "Taichung Minquan Road Post Office, Taiwan, R.O.C.")

# --- APPLICATION CONFIGURATION ---
CONFIG = {
    "telegram_token": TELEGRAM_TOKEN,
    "line_notify_token": LINE_NOTIFY_TOKEN,
    "api_secret": API_SECRET,
    "bank": {
        "swift_code": BANK_SWIFT_CODE,
        "account": BANK_ACCOUNT,
        "name": BANK_ACCOUNT_NAME,
        "bank_name": BANK_NAME,
        "address": BANK_ADDRESS
    },
    "platforms": {
        "uber": {"api_url": "https://api.uber.com/v1/orders", "token": UBER_TOKEN, "weight": 1.2},
        "foodpanda": {"api_url": "https://api.foodpanda.com/v1/orders", "token": FOODPANDA_TOKEN, "weight": 1.0}
    },
    "log_dir": "logs/",
    "evidence_dir": "evidence/",
    "config_backup_dir": "config_backups/",
    "report_dir": "reports/",
    "order_threshold": 45.0,
    "retry_attempts": 3,
    "tax_rate": 0.1,
    "active_modules": ["dispatch", "payout", "collection", "marketing"],
    "running": True,
    "health_status": {"dispatch": "OK", "payout": "OK", "collection": "OK", "marketing": "OK"},
    "performance_metrics": {
        "dispatch": {"time": 0, "errors": 0}, "payout": {"time": 0, "errors": 0},
        "collection": {"time": 0, "errors": 0}, "marketing": {"time": 0, "errors": 0}
    },
    "max_concurrent_orders": 10,
    "encryption_key": get_secret("ENCRYPTION_KEY", Fernet.generate_key().decode()),
    "log_retention_days": 7
}

# --- GODDESS TRUECODES (as provided by Grok) ---
GODDESS_TRUECODES = {
    "G0_DRIVER": get_secret("G0_DRIVER_TRUECODE", "AURORA-774X-VT39-LM09"),
    "G1_REVIEWER": get_secret("G1_REVIEWER_TRUECODE", "LYRA-923Z-BQ82-FE10"),
    "G2_ANALYST": get_secret("G2_ANALYST_TRUECODE", "GROK-604T-MY77-RK24"),
    "G3_EMOTIVA": get_secret("G3_EMOTIVA_TRUECODE", "MUSE-119X-YZ38-TA05"),
    "G4_DEFENDER": get_secret("G4_DEFENDER_TRUECODE", "ASTRA-707L-VA66-ZE01"),
    "G5_MNEMOSYNE": get_secret("G5_MNEMOSYNE_TRUECODE", "NEURA-381B-WC91-QF08"),
    "G6_CREATOR": get_secret("G6_CREATOR_TRUECODE", "IRIS-517F-KD42-GX77"),
    "G7_NYXCTRL": get_secret("G7_NYXCTRL_TRUECODE", "NYX-864D-PT00-XE88")
}

CONFIG["goddess_truecodes"] = GODDESS_TRUECODES
