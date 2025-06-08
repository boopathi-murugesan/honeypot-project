from email.message import EmailMessage
from dotenv import load_dotenv
from datetime import datetime
import os
import requests
import smtplib

# === Load .env credentials ===
load_dotenv()
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# === Log file path ===
LOG_FILE = "logs/honeypot.log"

# === Email Function ===
def send_email_log():
    try:
        if not EMAIL_USER or not EMAIL_PASS:
            print("[!] Email credentials missing.")
            return

        with open(LOG_FILE, "r") as f:
            log_content = f.read()

        msg = EmailMessage()
        msg.set_content(log_content)
        msg["Subject"] = f"Honeypot Log Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        msg["From"] = EMAIL_USER
        msg["To"] = EMAIL_USER  

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)

        print("[✓] Email sent successfully.")
    except Exception as e:
        print(f"[!] Failed to send email: {e}")

# === Telegram Function ===
def send_telegram_log():
    try:
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            print("[!] Telegram credentials missing.")
            return

        with open(LOG_FILE, "r") as f:
            log_content = f.read()

        # Limit to last 4000 chars (Telegram max limit for message)
        if len(log_content) > 4000:
            log_content = log_content[-4000:]

        def escape_markdown(text):
            escape_chars = r"_*[]()~`>#+-=|{}.!\\"
            return ''.join(['\\' + c if c in escape_chars else c for c in text])

        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": f"*Honeypot Live Log Report*\n\n{escape_markdown(log_content)}",
            "parse_mode": "MarkdownV2"
        }

        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        response = requests.post(url, data=payload)
        payload = {
    "chat_id": TELEGRAM_CHAT_ID,
    "text": "Unauthorized access detected",
}

        if response.status_code == 200:
            print("[✓] Telegram report sent successfully.")
        else:
            print(f"[!] Telegram error: {response.text}")
    except Exception as e:
        print(f"[!] Failed to send Telegram report: {e}")

# === Main Execution ===
if __name__ == "__main__":
    if not os.path.exists(LOG_FILE):
        print(f"[!] Log file not found: {LOG_FILE}")
        exit(1)

    send_email_log()
    send_telegram_log()
