import os
import time
import libtorrent as lt
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Telegram Bot Token
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
# Download directory
DOWNLOAD_DIR = "./downloads/"

# Initialize downloads directory
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a magnet link to download the torrent")

async def handle_magnet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    magnet_link = update.message.text
    msg = await update.message.reply_text("Starting download...")
    
    try:
        # Create torrent session
        ses = lt.session()
        ses.listen_on(6881, 6891)
        
        # Add magnet link
        params = {
            'save_path': DOWNLOAD_DIR,
            'storage_mode': lt.storage_mode_t.storage_mode_sparse,
            'paused': False,
            'auto_managed': True,
            'duplicate_is_error': True
        }
        
        handle = lt.add_magnet_uri(ses, magnet_link, params)
        
        # Wait for metadata
        await context.bot.edit_message_text(
            "Downloading metadata...",
            chat_id=msg.chat_id,
            message_id=msg.message_id
        )
        
        while not handle.has_metadata():
            time.sleep(1)
        
        # Get torrent info
        torinfo = handle.get_torrent_info()
        file_name = torinfo.name()
        
        # Wait for download to complete
        await context.bot.edit_message_text(
            f"Downloading: {file_name}",
            chat_id=msg.chat_id,
            message_id=msg.message_id
        )
        
        while handle.status().state != lt.torrent_status.seeding:
            s = handle.status()
            progress = s.progress * 100
            await context.bot.edit_message_text(
                f"Progress: {progress:.2f}% - {s.download_rate / 1000} kB/s",
                chat_id=msg.chat_id,
                message_id=msg.message_id
            )
            time.sleep(5)
        
        # Get first file path (for multi-file torrents, you might want to zip them)
        file_path = os.path.join(DOWNLOAD_DIR, file_name)
        
        # Send file back to user
        await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=open(file_path, 'rb'),
            filename=file_name,
            caption="Here's your downloaded file!"
        )
        
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

if __name__ == "__main__":
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_magnet))
    
    application.run_polling()
