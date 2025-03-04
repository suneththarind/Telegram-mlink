import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from youtubesearchpython import VideosSearch
from pytube import YouTube

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram Bot Token
TOKEN = '7929307746:AAFALj0ptgbheb0KIzJLZ3gbbwmv558qQbk'

def start(update: Update, context: CallbackContext):
    """Send a message when the command /start is issued."""
    update.message.reply_text(
        'Hi! Send me a song name and I will try to download it for you!\n\n'
        '⚠️ Please ensure you have the rights to download any content you request.'
    )

def help_command(update: Update, context: CallbackContext):
    """Send a message when the command /help is issued."""
    update.message.reply_text(
        'Just send me the name of the song you want to download. '
        'I will search YouTube and send you the best match!'
    )

def search_song(update: Update, context: CallbackContext):
    """Search for a song and download the audio."""
    query = update.message.text
    if not query:
        update.message.reply_text("Please send a song name.")
        return

    try:
        # Search YouTube for the query
        videos_search = VideosSearch(query, limit=1)
        results = videos_search.result()
        
        if not results['result']:
            update.message.reply_text("No results found 😢")
            return

        video_url = results['result'][0]['link']
        video_title = results['result'][0]['title']

        # Download audio using pytube
        yt = YouTube(video_url)
        audio_stream = yt.streams.filter(only_audio=True, file_extension='mp4').first()
        
        if not audio_stream:
            update.message.reply_text("Couldn't find an audio stream.")
            return

        # Download the file
        update.message.reply_text(f"Downloading: {video_title}...")
        audio_file = audio_stream.download(output_path='downloads/')
        
        # Rename file
        base, ext = os.path.splitext(audio_file)
        new_file = base + '.mp3'
        os.rename(audio_file, new_file)
        
        # Send the audio file
        with open(new_file, 'rb') as audio:
            update.message.reply_audio(audio, caption=video_title)
        
        # Clean up files
        os.remove(new_file)

    except Exception as e:
        logger.error(f"Error: {e}")
        update.message.reply_text("Something went wrong. Please try again later.")

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Register commands
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))

    # Register message handler
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, search_song))

    # Create downloads directory if not exists
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
