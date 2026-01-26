import os
import asyncio
import threading
import requests
import asyncpg
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from dotenv import load_dotenv

load_dotenv()

# --- CONFIG ---
BOT_TOKEN = os.getenv("BOT_BOT")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
SOL_MAIN = os.getenv("SOL_MAIN")
VIP_CHANNEL_ID = os.getenv("VIP_CHANNEL_ID")
DATABASE_URL = os.getenv("DATABASE_URL")
HELIUS_RPC = os.getenv("HELIUS_RPC")
REQUIRED_INVITES = 3

# --- FLASK SERVER (For Render Health Check) ---
flask_app = Flask(__name__)
@flask_app.route('/')
def health(): return "ICEGODS SYSTEM ACTIVE 🟢", 200

# --- DATABASE ENGINE ---
async def init_db():
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS ice_users (
                user_id BIGINT PRIMARY KEY,
                username TEXT,
                invites INTEGER DEFAULT 0,
                paid BOOLEAN DEFAULT FALSE
            )
        """)
        await conn.close()
        print("✅ Supabase Database Connected")
    except Exception as e:
        print(f"⚠️ DB Error: {e}")

# --- HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username

    conn = await asyncpg.connect(DATABASE_URL)
    user = await conn.fetchrow("SELECT invites, paid FROM ice_users WHERE user_id = $1", user_id)

    if not user:
        if context.args and context.args[0].isdigit():
            referrer = int(context.args[0])
            await conn.execute("UPDATE ice_users SET invites = invites + 1 WHERE user_id = $1", referrer)
        await conn.execute("INSERT INTO ice_users (user_id, username) VALUES ($1, $2)", user_id, username)
        invites, paid = 0, False
    else:
        invites, paid = user['invites'], user['paid']
    await conn.close()

    status = "ACTIVE ✅" if (paid or invites >= REQUIRED_INVITES) else "LOCKED 🔒"
    text = f"❄️ **ICEGODS TERMINAL** ❄️\n\n👤 @{username}\n👥 Invites: {invites}/{REQUIRED_INVITES}\n💎 Status: {status}"

    kb = [[InlineKeyboardButton("📤 Get Link", callback_data="get_link")],
          [InlineKeyboardButton("⚡ Unlock (0.5 SOL)", callback_data="pay_instant")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tx = context.args[0] if context.args else ""
    if not tx: return await update.message.reply_text("❌ Send TX ID.")

    # Helius Check
    res = requests.post(HELIUS_RPC, json={"jsonrpc":"2.0","id":1,"method":"getTransaction","params":[tx,{"encoding":"json","maxSupportedTransactionVersion":0}]}).json()
    if res.get("result"):
        conn = await asyncpg.connect(DATABASE_URL)
        await conn.execute("UPDATE ice_users SET paid = TRUE WHERE user_id = $1", update.effective_user.id)
        await conn.close()
        await update.message.reply_text("✅ **VERIFIED!** VIP Alpha Unlocked.")
    else:
        await update.message.reply_text("❌ TX not found.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "get_link":
        await query.message.reply_text(f"📤 **Link:** `https://t.me/{context.bot.username}?start={query.from_user.id}`")
    elif query.data == "pay_instant":
        await query.message.reply_text(f"💳 Send **0.5 SOL** to:\n`{SOL_MAIN}`\n\nReply: `/verify <TX_ID>`")

# --- RUNNERS ---
def run_flask():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)

async def run_bot():
    await init_db()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("verify", verify))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("🚀 BOT POLLING STARTED")
    async with app:
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        while True: await asyncio.sleep(3600)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    asyncio.run(run_bot())
