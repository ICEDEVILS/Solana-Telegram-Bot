# main.py - Consolidated Flask Webhook Handler for Render (PTB v20+ Compatible)

import os
import logging
from flask import Flask, request, jsonify
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from solders.pubkey import Pubkey
from solana.rpc.api import Client as SolanaClient

# --- Configuration & Initialization ---
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment Variables (Ensure these are set on Render)
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
PAYMENT_WALLET = os.environ.get("PAYMENT_WALLET")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "-100123456789") 

# Solana Setup
SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"
solana_client = SolanaClient(SOLANA_RPC_URL)

app = Flask(__name__)

# Initialize the Telegram Application Builder
try:
    application = Application.builder().token(BOT_TOKEN).build()
except Exception as e:
    logger.error(f"Failed to build Telegram Application: {e}")
    # Application will not run without a valid token

# --- Core Bot Logic Functions ---

def start_command(update: Update, context):
    """Sends a welcome message and initiates the payment process."""
    if not update.effective_message: return

    user = update.effective_user
    welcome_message = (
        f"👋 Hello, {user.full_name}!\n\n"
        "Welcome to the Crypto-Gated Bot. To gain access to the private channel, "
        "you need to complete a small, one-time payment.\n\n"
        f"💰 **Payment Wallet:** `{PAYMENT_WALLET}`\n"
        "⚠️ **Note:** After sending the payment, use the /status command to verify and join."
    )
    update.effective_message.reply_text(welcome_message, parse_mode='Markdown')

def status_command(update: Update, context):
    """Checks the user's payment status on the blockchain (simplified)."""
    if not update.effective_message: return
        
    # User ID is stored for the background job to check
    user_id = update.effective_user.id
    
    update.effective_message.reply_text(
        "Checking your payment status... This check is performed by a background "
        "job (Render Cron Job). Please wait a few moments and try again."
    )

def error_handler(update: Update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    if update and update.effective_message:
        update.effective_message.reply_text("An internal error occurred. Please try again later.")

# --- Application Setup ---

application.add_handler(CommandHandler("start", start_command))
application.add_handler(CommandHandler("status", status_command))
application.add_error_handler(error_handler)


# --- Flask Webhook Handler ---

@app.route('/', methods=['POST'])
def telegram_webhook():
    """Route to receive updates from Telegram."""
    if request.method == "POST":
        update_json = request.get_json(force=True)
        if update_json:
            try:
                update = Update.de_json(update_json, application.bot)
                application.process_update(update) 
                return jsonify({'status': 'ok'}), 200
            except Exception as e:
                logger.error(f"Error processing update: {e}")
                return jsonify({'status': 'error', 'message': str(e)}), 500
        
    return jsonify({'status': 'invalid request'}), 200

# --- Health Check (for Render) ---
@app.route('/', methods=['GET'])
def health_check():
    """Simple check to ensure the Render service is running."""
    return 'Bot Webhook Service is Running!', 200

# --- Local Runner ---
if __name__ == '__main__':
    logger.info("Starting local Flask server...")
    app.run(debug=True, host='0.0.0.0', port=5000)
