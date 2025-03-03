import os
from urllib.parse import urlparse, parse_qs
from base64 import b32encode
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

load_dotenv()  # Load environment variables
BOT_TOKEN = os.getenv("7987139723:AAGbf6Vve5CNJXZsgugTMk9NDzLLB2f6b74")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔍 Send me a Magnet Link to analyze!\n"
        "Example: magnet:?xt=urn:btih:08ada5a7a6183aae1e09d831df6748d566095a10..."
    )

async def handle_magnet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        magnet_uri = update.message.text.strip()
        
        if not magnet_uri.startswith("magnet:?"):
            await update.message.reply_text("❌ Invalid format! Must start with 'magnet:?'")
            return

        parsed = urlparse(magnet_uri)
        params = parse_qs(parsed.query)

        # Extract parameters with defaults
        xt = params.get('xt', [''])[0]
        dn = params.get('dn', ['No name provided'])[0]
        tr = params.get('tr', [])
        
        # Process info hash
        info_hash = "N/A"
        if xt.startswith("urn:btih:"):
            raw_hash = xt[9:]
            if len(raw_hash) == 32:  # Base32 encoded
                info_hash = b32encode(raw_hash.upper().encode()).hex().lower()
            else:  # HEX format
                info_hash = raw_hash.lower()

        # Build response
        response = (
            "🧲 **Magnet Link Analysis**\n"
            f"• **Name**: `{dn}`\n"
            f"• **Info Hash**: `{info_hash}`\n"
            f"• **Trackers Found**: {len(tr)}\n"
        )
        
        if tr:
            response += "\n**Top Trackers**:\n"
            for idx, tracker in enumerate(tr[:3], 1):
                response += f"  {idx}. `{tracker}`\n"
        
        await update.message.reply_text(response, parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {str(e)}")

if __name__ == "__main__":
    if not BOT_TOKEN:
        raise ValueError("Missing TELEGRAM_BOT_TOKEN in environment!")
    
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_magnet))
    print("Bot is running...")
    app.run_polling()
