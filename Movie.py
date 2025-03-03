import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# TMDB API configTon
TMDB_API_KEY = "267e38d9f7dd69a9f609d281ed878515"  # Get yours from https://www.themoviedb.org/settings/api
TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
TMDB_DETAILS_URL = "https://api.themoviedb.org/3/movie"
TMDB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to Movie Bot! 🎬\nEnter a movie name to get its details and poster.")

def search_movie(movie_name: str):
    params = {
        "api_key": TMDB_API_KEY,
        "query": movie_name,
        "language": "en-US"
    }
    response = requests.get(TMDB_SEARCH_URL, params=params)
    data = response.json()
    return data.get("results")[0] if data.get("results") else None

def get_movie_details(movie_id: int):
    params = {
        "api_key": TMDB_API_KEY,
        "language": "en-US"
    }
    response = requests.get(f"{TMDB_DETAILS_URL}/{movie_id}", params=params)
    return response.json() if response.status_code == 200 else None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    movie_name = update.message.text
    try:
        # Search for the movie
        movie_data = search_movie(movie_name)
        if not movie_data:
            await update.message.reply_text("Movie not found! 😢")
            return

        # Get detailed information
        details = get_movie_details(movie_data["id"])
        
        # Prepare movie information
        title = details.get("title", "N/A")
        overview = details.get("overview", "No overview available")
        rating = details.get("vote_average", "N/A")
        release_date = details.get("release_date", "N/A")
        genres = ", ".join([g["name"] for g in details.get("genres", [])])
        poster_path = details.get("poster_path")

        # Create caption text
        caption = (
            f"🎬 <b>{title}</b> ({release_date[:4] if release_date else 'N/A'})\n\n"
            f"⭐ Rating: {rating}/10\n"
            f"📚 Genres: {genres}\n\n"
            f"📖 Overview:\n{overview}"
        )

        # Send photo with caption
        if poster_path:
            poster_url = f"{TMDB_IMAGE_URL}{poster_path}"
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=poster_url,
                caption=caption,
                parse_mode="HTML"
            )
        else:
            await update.message.reply_text(caption, parse_mode="HTML")

    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("Something went wrong. Please try again later. 😢")

if __name__ == "__main__":
    # Set up Telegram bot
    TOKEN = "7987139723:AAGbf6Vve5CNJXZsgugTMk9NDzLLB2f6b74"  # Get from @BotFather
    application = Application.builder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start bot
    print("Bot is running...")
    application.run_polling()
