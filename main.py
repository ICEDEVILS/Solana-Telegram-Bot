import os
import asyncio
import threading
import random
import requests
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

# --- CONFIGURATION (Load from Env) ---
BOT_TOKEN = os.getenv("BOT_BOT")
SOL_MAIN = os.getenv("SOL_MAIN") # Your Wallet
VIP_CHANNEL_ID = os.getenv("VIP_CHANNEL_ID") # e.g. -1002384609234
ADMIN_ID = os.getenv("ADMIN_ID")

# --- FLASK WEB SERVER (Health Check for Render) ---
flask_app = Flask(__name__)
@flask_app.route('/')
def health(): return "BOOST LEGENDS CORE ONLINE 🟢", 200

def run_web():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)

# --- 🟢 REVENUE FEATURE 1: AUTOMATED BUY ALERTS ---
# This makes the channel look institutional and high-volume
async def post_buy_alerts(context: ContextTypes.DEFAULT_TYPE):
    tokens = [
        {"name": "Club Penguin", "sym": "CPENG", "mc": "$1,084,104"},
        {"name": "Eva Everywhere", "sym": "EVA", "mc": "$2,076,345"},
        {"name": "Cummingtonite", "sym": "CUM", "mc": "$3,154,662"},
        {"name": "Copper Inu", "sym": "COPPERINU", "mc": "$6,559,197"}
    ]
    t = random.choice(tokens)
    sol_amt = round(random.uniform(0.8, 12.5), 3)
    usdc_amt = round(sol_amt * 108, 2) # Calculated on current SOL price
    circles = "🟢" * random.randint(8, 25)

    msg = (
        f"⏺ | {t['name']} / {t['sym']}\n"
        f"{circles}\n\n"
        f"🔀 ${usdc_amt:,} ({sol_amt} SOL)\n"
        f"👤 Buyer / [TX](https://solscan.io)\n"
        f"🪙 Position +{random.randint(15, 450)}%\n"
        f"💸 Market Cap {t['mc']}\n\n"
        f"DexT | Screener | [Buy](https://t.me/{context.bot.username}) | [Trending](https://t.me/{context.bot.username})"
    )
    try:
        await context.bot.send_message(chat_id=VIP_CHANNEL_ID, text=msg, parse_mode="Markdown", disable_web_page_preview=True)
    except Exception as e:
        print(f"Alert Error: {e}")

# --- 🚀 REVENUE FEATURE 2: SERVICE ADS (High Ticket) ---
async def post_service_ads(context: ContextTypes.DEFAULT_TYPE):
    ad_type = random.choice(["trending", "volume"])

    if ad_type == "trending":
        msg = (
            "🔥 **BOOST LEGENDS Dexscreener Trending Service**\n"
            "Push your token to top #10 trending!\n\n"
            "📊 **What You Get**\n"
            "✨ Token pushed to top #10 trending\n"
            "👀 Maximum visibility to thousands of active traders\n"
            "📈 Increased organic discovery\n"
            "💰 **Price:** 1200 - 1700 USDT/USDC\n\n"
            "━━━━━━━━━━━━━━━\n"
            "👇 Click below to start Trending Order:"
        )
    else:
        msg = (
            "🚀 **BOOST LEGENDS Volume Booster**\n"
            "Boost your token's volume smartly!\n\n"
            "💡 **Why Choose Us?**\n"
            "🏆 Cheapest on the market\n"
            "📉 Chart-safe, no pump/dump\n"
            "🧠 AI-powered adaptive behavior\n\n"
            "━━━━━━━━━━━━━━━\n"
            "👇 Click below to setup Volume Bot:"
        )

    kb = [[InlineKeyboardButton("💳 OPEN ORDER TERMINAL", url=f"https://t.me/{context.bot.username}")]]
    try:
        await context.bot.send_message(chat_id=VIP_CHANNEL_ID, text=msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
    except Exception as e:
        print(f"Ad Error: {e}")

# --- 🤖 REVENUE FEATURE 3: THE ORDER TERMINAL ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "❄️ **ICEGODS INSTITUTIONAL TERMINAL** ❄️\n\n"
        "Welcome to the high-frequency revenue hub. Select a service to begin deployment:\n\n"
        "1️⃣ **Trending Service** ($1200 - $1700)\n"
        "2️⃣ **Volume Booster** (1 SOL+)\n"
        "3️⃣ **Whale Alpha Access** (0.5 SOL)"
    )
    kb = [
        [InlineKeyboardButton("🔥 ORDER TRENDING", callback_data="order_trending")],
        [InlineKeyboardButton("📈 SETUP VOLUME BOT", callback_data="order_volume")],
        [InlineKeyboardButton("💎 PREMIUM ALPHA ACCESS", callback_data="order_alpha")]
    ]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "order_trending":
        await query.message.reply_text(
            "📉 **TRENDING PROTOCOL**\n\n"
            "Please send **1200 USDT/USDC** to:\n"
            f"`{SOL_MAIN}`\n\n"
            "After payment, send your Token CA and wait for Admin confirmation.",
            parse_mode="Markdown"
        )
    elif query.data == "order_alpha":
        await query.message.reply_text(
            "💎 **ALPHA ACCESS PROTOCOL**\n\n"
            "Send **0.5 SOL** to:\n"
            f"`{SOL_MAIN}`\n\n"
            "Reply with `/verify <TX_ID>` to unlock the VIP channel.",
            parse_mode="Markdown"
        )

# --- EXECUTION ENGINE ---
if __name__ == "__main__":
    # 1. Start Web Server
    threading.Thread(target=run_web, daemon=True).start()

    # 2. Build Application
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # 3. Add Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    # 4. START REVENUE AUTOMATION
    if app.job_queue:
        # Post a Buy Alert every 8 minutes
        app.job_queue.run_repeating(post_buy_alerts, interval=480, first=10)
        # Post a Service Ad every 35 minutes
        app.job_queue.run_repeating(post_service_ads, interval=2100, first=30)

    print("🚀 ICEGODS REVENUE WEAPON ACTIVE")
    app.run_polling(drop_pending_updates=True)
