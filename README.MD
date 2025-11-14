
---

## 📝 2. `README.md` Content

This file provides a clear overview, setup instructions, and required environment variables for anyone (including the Render service) using your repository.

| File Name | Content |
| :--- | :--- |
| **`README.md`** | ```markdown
# 🔱 Solana Crypto-Gated Telegram Bot (IceDevils Bot)

This is a Python-based Telegram bot designed to grant users access to a private channel upon verifying a Solana token or SOL payment to a designated wallet. It is built using the modern `python-telegram-bot` framework and Flask for webhook handling.

## 🚀 Deployment

The project is structured for easy deployment on **Render**, split into two separate services:
1.  **Web Service:** Runs the `main.py` webhook handler (via Gunicorn).
2.  **Cron Job:** Runs the `scanner_job.py` periodically for payment verification and user management.

## ⚙️ Required Environment Variables

The following environment variables **MUST** be set on **BOTH** the Render Web Service and the Render Cron Job:

| Variable | Description |
| :--- | :--- |
| `TELEGRAM_BOT_TOKEN` | The unique token obtained from BotFather. |
| `PAYMENT_WALLET` | The Solana Public Key where users must send payments. |
| `CHANNEL_ID` | The Telegram ID of the private channel (e.g., `-100123456789`). |
``` |

---

## 💻 Recommended Next Steps

1.  **Create Files on GitHub:** Go to your repository on the GitHub website (`https://github.com/ICEDEVILS/Solana-Telegram-Bot`).
2.  **Create New File:** Click **"Add file"** > **"Create new file"** and paste the content for `.gitignore`, `README.md`, and confirm the content for **`main.py`**, **`Procfile`**, **`requirements.txt`**, and **`scanner_job.py`**.
3.  **Clone Clean Repo:** Once all files are committed on GitHub, delete your local Termux folder and clone the repository back down.

```bash
cd ~
rm -rf Solana-Telegram-Bot  # Removes the old, incomplete folder
git clone https://github.com/ICEDEVILS/Solana-Telegram-Bot.git
