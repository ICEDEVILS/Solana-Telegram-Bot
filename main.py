import os, random, asyncio, threading, sqlite3
from datetime import datetime
from flask import Flask
from solana.rpc.api import Client
from solders.signature import Signature
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
from dotenv import load_dotenv

load_dotenv()

# --- CONFIG ---
BOT_TOKEN = os.getenv("BOT_BOT")
SOL_MAIN = os.getenv("SOL_MAIN")
VIP_CHANNEL_ID = os.getenv("VIP_CHANNEL_ID")
ADMIN_ID = os.getenv("ADMIN_ID")
RPC_URL = os.getenv("HELIUS_RPC")
REQUIRED_INVITES = 3
client = Client(RPC_URL)

# --- WEB SERVER FOR RENDER ---
flask_app = Flask(__name__)
@flask_app.route("/")
def health(): return "ICE REIGN WEAPON ACTIVE 🟢", 200
def run_web():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)

# --- LOCAL DATABASE (SQLite) ---
def init_db():
    conn = sqlite3.connect('icegods.db')
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT, invites INTEGER DEFAULT 0, paid INTEGER DEFAULT 0)")
    conn.commit()
    conn.close()

# --- THE WEAPON HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username

    conn = sqlite3.connect('icegods.db')
    cur = conn.cursor()

    cur.execute("SELECT invites, paid FROM users WHERE user_id = ?", (user_id,))
    user = cur.fetchone()

    if not user:
        if context.args and context.args[0].isdigit():
            referrer = int(context.args[0])
            cur.execute("UPDATE users SET invites = invites + 1 WHERE user_id = ?", (referrer,))
            try: await context.bot.send_message(referrer, "🔥 **NEW RECRUIT!** Someone joined using your link.")
            except: pass

        cur.execute("INSERT INTO users (user_id, username, invites, paid) VALUES (?, ?, 0, 0)", (user_id, username))
        conn.commit()
        invites, paid = 0, 0
    else:
        invites, paid = user

    ref_link = f"https://t.me/{context.bot.username}?start={user_id}"
    text = (
        "❄️ **ICEGODS INTELLIGENCE TERMINAL** ❄️\n\n"
        f"👤 **User:** @{username}\n"
        f"👥 **Invites:** {invites}/{REQUIRED_INVITES}\n"
        f"💎 **VIP Status:** {'ACTIVE ✅' if (paid == 1 or invites >= REQUIRED_INVITES) else 'LOCKED 🔒'}\n\n"
        "Invite 3 friends or pay for instant access to 100x Gem Calls."
    )
    kb = [
        [InlineKeyboardButton("📤 Get My Referral Link", callback_data="get_link")],
        [InlineKeyboardButton("⚡ Instant Unlock (0.2 SOL)", callback_data="pay_instant")],
        [InlineKeyboardButton("💎 Enter VIP Channel", url="https://t.me/ICEGODSICEDEVILS")]
    ]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
    conn.close()

async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: `/verify <TX>`")
    sig_str = context.args[0]
    await update.message.reply_text("📡 **Scanning Blockchain...**")

    try:
        sig = Signature.from_string(sig_str)
        tx = client.get_transaction(sig, max_supported_transaction_version=0)
        if tx.value:
            conn = sqlite3.connect('icegods.db'); cur = conn.cursor()
            cur.execute("UPDATE users SET paid = 1 WHERE user_id = ?", (update.effective_user.id,))
            conn.commit(); conn.close()
            await update.message.reply_text(f"✅ **PAYMENT VERIFIED!**\nWelcome to the Inner Circle.")
        else:
            await update.message.reply_text("❌ Transaction not found. Check SolScan.")
    except:
        await update.message.reply_text("❌ Invalid Signature.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer()
    if query.data == "get_link":
        await query.message.reply_text(f"📤 **Share to unlock Alpha:**\n`https://t.me/{context.bot.username}?start={query.from_user.id}`")
    elif query.data == "pay_instant":
        await query.message.reply_text(f"💳 **INSTANT ACCESS**\n\nSend **0.2 SOL** to:\n`{SOL_MAIN}`\n\nReply with: `/verify <TX_HASH>`")

if __name__ == "__main__":
    init_db()
    threading.Thread(target=run_web, daemon=True).start()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("verify", verify))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("🚀 ICEGODS VIRAL WEAPON ACTIVE")
    app.run_polling()
