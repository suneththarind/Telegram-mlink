import os
import tempfile
import aiohttp
from aiohttp import web
from pytube import YouTube

# Initialize your Pella bot
BOT_TOKEN = os.environ.get("7929307746:AAHu9MUWhE8NgRy2JVyAU-9GK2UXz6b8kEc")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

async def handle_download(request):
    data = await request.json()
    message = data.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    url = message.get("text")

    if not url or ("youtube.com" not in url and "youtu.be" not in url):
        return await send_message(chat_id, "Please send a valid YouTube URL.")

    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            yt = YouTube(url)
            stream = yt.streams.filter(progressive=True, file_extension="mp4").order_by("resolution").desc().first()
            
            if not stream:
                return await send_message(chat_id, "No suitable video stream found.")

            file_path = stream.download(output_path=tmp_dir)
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            
            if file_size > 50:
                return await send_message(chat_id, "File too large (max 50MB allowed).")

            async with aiohttp.ClientSession() as session:
                with open(file_path, "rb") as video_file:
                    form_data = aiohttp.FormData()
                    form_data.add_field("video", video_file, filename=os.path.basename(file_path))
                    await session.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo",
                        data={
                            "chat_id": chat_id,
                            "caption": "Here's your YouTube video!",
                            "video": form_data["video"]
                        }
                    )

        return web.Response(text="OK")

    except Exception as e:
        return await send_message(chat_id, f"Error: {str(e)}")

async def send_message(chat_id, text):
    async with aiohttp.ClientSession() as session:
        await session.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": text}
        )
    return web.Response(text="OK")

async def handle_updates(request):
    if request.method == "POST":
        return await handle_download(request)
    return web.Response(text="OK")

def create_app():
    app = web.Application()
    app.router.add_post("/", handle_updates)
    return app

if __name__ == "__main__":
    web.run_app(create_app(), port=int(os.environ.get("PORT", 3000)))
