import os
import asyncio
import threading
import random
import requests
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from dotenv import load_dotenv

load_dotenv()

# --- CONFIG ---
BOT_TOKEN = os.getenv("BOT_BOT")
ADMIN_ID = os.getenv("ADMIN_ID")
SOL_MAIN = os.getenv("SOL_MAIN")
VIP_CHANNEL_ID = os.getenv("VIP_CHANNEL_ID")
HELIUS_RPC = os.getenv("HELIUS_RPC")

# --- FLASK SERVER (For Render Health Check) ---
flask_app = Flask(__name__)
@flask_app.route('/')
def health(): return "ICEGODS HUNTER ENGINE ONLINE 🟢", 200

def run_web():
    # This is the function Render looks for to keep the bot alive
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)

# --- HUNTER ENGINE (Automated Alpha Alerts) ---
async def post_whale_alerts(context: ContextTypes.DEFAULT_TYPE):
    """This function posts 100x Gem alerts to your channel automatically"""
    tokens = ["$ICE", "$SOL", "$WIF", "$JUP", "$BONK", "$POPCAT", "$PENGU"]
    token = random.choice(tokens)
    amount = random.randint(45, 650)

    msg = (
        f"🚨 **WHALE BUY DETECTED** 🐋\n\n"
        f"💰 **Amount:** {amount} SOL\n"
        f"🪙 **Token:** `[HIDDEN - UNLOCK IN BOT]`\n"
        f"🛡️ **Safety Score:** {random.randint(90, 99)}%\n\n"
        f"🔥 **Unlock the Alpha here:**\n"
        f"👉 @{context.bot.username}\n"
        f"👉 @{context.bot.username}"
    )

    try:
        # Posts to your VIP/Public channel
        await context.bot.send_message(chat_id=VIP_CHANNEL_ID, text=msg, parse_mode="Markdown")
        print(f"✅ Alert posted for {token}")
    except Exception as e:
        print(f"❌ Alert Error: {e}")

# --- BOT HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username or "Warrior"
    text = (
        f"❄️ **ICEGODS INTELLIGENCE TERMINAL** ❄️\n\n"
        f"👤 **User:** @{username}\n"
        f"💎 **VIP Status:** LOCKED 🔒\n\n"
        "To unlock the token address and AI safety audit for our latest whale alerts, you must:\n\n"
        "1️⃣ Invite 3 friends using your link\n"
        "2️⃣ Or pay **0.5 SOL** for Lifetime Access."
    )
    kb = [[InlineKeyboardButton("📤 Get My Referral Link", callback_data="get_link")],
          [InlineKeyboardButton("⚡ Instant Unlock (0.5 SOL)", callback_data="pay_instant")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: `/verify <TX_ID>`")
    tx_id = context.args[0]
    await update.message.reply_text("📡 **Scanning Solana Blockchain...**")

    # Real Helius Verification logic
    payload = {"jsonrpc": "2.0", "id": 1, "method": "getTransaction", "params": [tx_id, {"encoding": "json", "maxSupportedTransactionVersion": 0}]}
    try:
        res = requests.post(HELIUS_RPC, json=payload).json()
        if res.get("result"):
            await update.message.reply_text("✅ **VERIFIED.** Welcome to the Inner Circle.")
        else:
            await update.message.reply_text("❌ TX not found. Try again in 60 seconds.")
    except:
        await update.message.reply_text("⚠️ Connection error. Try again.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer()
    if query.data == "get_link":
        link = f"https://t.me/{context.bot.username}?start={query.from_user.id}"
        await query.message.reply_text(f"📤 **Your Link:**\n`{link}`")
    elif query.data == "pay_instant":
        await query.message.reply_text(f"💳 Send **0.5 SOL** to:\n`{SOL_MAIN}`\n\nReply: `/verify <TX_ID>`")

# --- MAIN ---
if __name__ == "__main__":
    # 1. Start Flask
    threading.Thread(target=run_web, daemon=True).start()

    # 2. Build App
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # 3. Add Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("verify", verify))
    app.add_handler(CallbackQueryHandler(button_handler))

    # 4. START THE HUNTER ALERTS
    # This will post an alert every 20 minutes (1200 seconds)
    if app.job_queue:
        app.job_queue.run_repeating(post_whale_alerts, interval=1200, first=10)

    print("🚀 ICEGODS HUNTER ENGINE ACTIVE")
    app.run_polling(drop_pending_updates=True)
