# scanner_job.py - Runs as a Render Cron Job to check payments and grant access

import os
import logging
import time
from telegram import Bot
from solana.rpc.api import Client as SolanaClient
from solders.pubkey import Pubkey
from solana.transaction import Transaction

# --- Configuration ---
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
PAYMENT_WALLET_STR = os.environ.get("PAYMENT_WALLET")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "-100123456789")

SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"
solana_client = SolanaClient(SOLANA_RPC_URL)
bot = Bot(token=BOT_TOKEN)

REQUIRED_PAYMENT_AMOUNT = 0.01  # Example: 0.01 SOL

# --- Core Scanner Logic ---

def check_solana_payments():
    """Checks the payment wallet for new transactions and grants channel access."""
    if not PAYMENT_WALLET_STR:
        logger.error("PAYMENT_WALLET environment variable is not set.")
        return

    try:
        # 1. Get the public key for the payment wallet
        payment_pubkey = Pubkey.from_string(PAYMENT_WALLET_STR)
        
        # 2. Fetch recent transactions
        # This is simplified; a real scanner tracks block height or signature history.
        signatures = solana_client.get_signatures_for_address(payment_pubkey, limit=10)
        
        if not signatures.value:
            logger.info("No recent transactions found on the payment wallet.")
            return

        for sig_info in signatures.value:
            tx_signature = sig_info.signature
            
            # 3. Check transaction details
            tx_details = solana_client.get_transaction(tx_signature, encoding="jsonParsed", max_supported_transaction_version=0)
            
            if not tx_details.value:
                continue
                
            # Process transaction logic (Simplified example: look for any transfer)
            # This is complex and requires deep transaction parsing. For demonstration:
            
            # --- SIMPLIFIED VERIFICATION ---
            # In a real bot, you'd check instruction types, recipient, and memo (for user ID).
            
            # For this example, we'll assume any recent transfer > 0.01 SOL is valid 
            # and that you track the user ID offline (e.g., in a DB/file)
            
            logger.info(f"Processing transaction: {tx_signature}")
            
            # 4. Mock Verification and Action
            # Since we cannot easily track which user sent which transaction without a database,
            # this part remains a placeholder showing the final Telegram action.
            
            # The bot would: 
            # a) Find the user_id associated with this payment.
            # b) Mark the payment as processed.
            # c) Add the user to the channel.
            
            # MOCK ACTION: If a valid payment was found, add a known user (placeholder for now)
            # try:
            #     known_user_id = 123456789  # Placeholder User ID that made a payment
            #     bot.promote_chat_member(chat_id=CHANNEL_ID, user_id=known_user_id, can_post_messages=True)
            #     bot.send_message(known_user_id, "✅ Payment verified! You now have access to the private channel.")
            #     logger.info(f"Access granted to user {known_user_id}")
            # except Exception as e:
            #     logger.error(f"Error granting access: {e}")
            
        logger.info("Solana payment scanning completed.")

    except Exception as e:
        logger.error(f"FATAL ERROR in scanner job: {e}")

# --- Runner ---
if __name__ == "__main__":
    logger.info("Starting Solana Payment Scanner Cron Job...")
    # This will run once per cron job execution
    check_solana_payments()
