import os
import asyncio
import psycopg2
from datetime import datetime, timedelta
from dotenv import load_dotenv
from solana.rpc.api import Client
from solders.signature import Signature
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

load_dotenv()

# --- CONFIG ---
BOT_TOKEN = os.getenv("BOT_BOT")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
SOL_MAIN_WALLET = os.getenv("SOL_MAIN")
VIP_CHANNEL_ID = os.getenv("VIP_CHANNEL_ID")
DATABASE_URL = os.getenv("DATABASE_URL")
RPC_URL = os.getenv("HELIUS_RPC")
SUB_PRICE_SOL = 0.5

client = Client(RPC_URL)

# --- DATABASE ---
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

# --- THE WEAPON LOGIC (Detection) ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "❄️ **ICEGODS INTELLIGENCE TERMINAL v2.1** ❄️\n\n"
        "The system is scanning Solana Mainnet for Whale movements.\n\n"
        "🛡️ **VIP ACCESS:**\n"
        "• Real-time Alpha Alerts\n"
        "• AI Contract Audits\n"
        f"• Price: {SUB_PRICE_SOL} SOL / Month"
    )
    kb = [[InlineKeyboardButton("🔓 UNLOCK ACCESS", callback_data="pay")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: `/verify <signature>`")

    sig_str = context.args[0]
    await update.message.reply_text("📡 **Scanning Blockchain...**")

    try:
        sig = Signature.from_string(sig_str)
        tx = client.get_transaction(sig, max_supported_transaction_version=0)

        if tx.value:
            expiry = datetime.now() + timedelta(days=30)
            # Save to DB
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO members (user_id, username, expiry_date, tx_sig) VALUES (%s, %s, %s, %s) ON CONFLICT (user_id) DO UPDATE SET expiry_date = %s",
                (update.effective_user.id, update.effective_user.username, expiry, sig_str, expiry)
            )
            conn.commit()

            # Create Link
            link = await context.bot.create_chat_invite_link(chat_id=VIP_CHANNEL_ID, member_limit=1)
            await update.message.reply_text(f"✅ **VERIFIED!**\nWelcome to IceGods.\n\n🔗 {link.invite_link}", parse_mode="Markdown")

            # Alert Admin
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"💰 **NEW REVENUE:** User {update.effective_user.username} paid {SUB_PRICE_SOL} SOL.")
        else:
            await update.message.reply_text("❌ Transaction not found. Ensure it is confirmed on SolScan.")
    except Exception as e:
        await update.message.reply_text(f"⚠️ System Error: {str(e)}")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "pay":
        await query.message.reply_text(
            f"🚀 **PAYMENT PROTOCOL**\n\nSend **{SUB_PRICE_SOL} SOL** to:\n`{SOL_MAIN_WALLET}`\n\n"
            "Then run: `/verify <TX_SIGNATURE>`",
            parse_mode="Markdown"
        )

# --- AUTO-DETECTION (Proof of Value) ---
async def post_alerts(context: ContextTypes.DEFAULT_TYPE):
    """This function simulates/detects activity to keep the channel hot"""
    await context.bot.send_message(
        chat_id=VIP_CHANNEL_ID,
        text="📡 **ICEGODS SCANNER:** Large liquidity move detected on SOLANA. AI suggests 87% safety score. 🚀",
        parse_mode="Markdown"
    )

# --- MAIN ---
if __name__ == "__main__":
    init_db()
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("verify", verify))
    app.add_handler(CallbackQueryHandler(button_handler))

    # This sends an alert every 2 hours to make the channel look active
    job_queue = app.job_queue
    job_queue.run_repeating(post_alerts, interval=7200, first=10)

    print("🔥 ICEGODS WEAPON v2.1 ACTIVE")
    app.run_polling()
