import os
import logging
from datetime import datetime, timedelta
import psycopg2
from dotenv import load_dotenv
from solana.rpc.api import Client
from solders.signature import Signature
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

# Setup logging
logging.basicConfig(level=logging.INFO)
load_dotenv()

# --- CONFIG ---
BOT_TOKEN = os.getenv("BOT_BOT")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
SOL_MAIN_WALLET = os.getenv("SOL_MAIN")
VIP_CHANNEL_ID = os.getenv("VIP_CHANNEL_ID")
DATABASE_URL = os.getenv("DATABASE_URL")
RPC_URL = os.getenv("HELIUS_RPC")
SUB_PRICE_SOL = 0.5  # Edit this to change your price

client = Client(RPC_URL)

# --- DB INIT ---
def init_db():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS members (
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            expiry_date TIMESTAMP,
            tx_sig TEXT
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

# --- PAYMENT CHECK ---
def check_tx(sig_str):
    try:
        sig = Signature.from_string(sig_str)
        # Verify transaction on-chain
        response = client.get_transaction(sig, max_supported_transaction_version=0)
        if response.value:
            # Add complex logic here if you want to verify exact SOL amount
            return True
        return False
    except Exception as e:
        logging.error(f"Payment Error: {e}")
        return False

# --- HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "⚔️ **ICEGODS INTELLIGENCE TERMINAL** ⚔️\n\n"
        "Access the most advanced Solana Whale tracking & Alpha calls.\n\n"
        f"💳 **Subscription:** {SUB_PRICE_SOL} SOL / 30 Days"
    )
    kb = [[InlineKeyboardButton("💳 PAY NOW", callback_data="pay")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "pay":
        msg = (
            "🚀 **SYSTEM AUTHORIZATION REQUIRED**\n\n"
            f"1. Send **{SUB_PRICE_SOL} SOL** to:\n`{SOL_MAIN_WALLET}`\n\n"
            "2. Copy the Transaction Signature (TXID).\n"
            "3. Use command: `/verify YOUR_SIGNATURE`"
        )
        await query.message.reply_text(msg, parse_mode="Markdown")

async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: `/verify <signature>`")

    sig = context.args[0]
    await update.message.reply_text("📡 Scanning Solana Blockchain...")

    if check_tx(sig):
        expiry = datetime.now() + timedelta(days=30)
        # Update Database
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO members (user_id, username, expiry_date, tx_sig) VALUES (%s, %s, %s, %s) ON CONFLICT (user_id) DO UPDATE SET expiry_date = %s",
            (update.effective_user.id, update.effective_user.username, expiry, sig, expiry)
        )
        conn.commit()

        # Invite Link
        link = await context.bot.create_chat_invite_link(chat_id=VIP_CHANNEL_ID, member_limit=1)

        await update.message.reply_text(
            f"✅ **ACCESS GRANTED**\n\nExpiry: {expiry.date()}\n🔗 **INVITE:** {link.invite_link}",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("❌ Transaction invalid or not confirmed yet.")

# --- APP ---
if __name__ == "__main__":
    init_db()
    print("🔥 ICEGODS WEAPON ACTIVE")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("verify", verify))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()
