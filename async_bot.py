import os
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler

TOKEN = os.environ.get("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN not set")

async def start(update: Update, context):
    await update.message.reply_text("✅ Bot is active. I will delete inappropriate content.")

def is_nsfw(image_url):
    try:
        r = requests.get(
            "https://api.sightengine.com/1.0/check.json",
            params={
                "models": "nudity-2.0,wad",
                "api_user": "demo",
                "api_secret": "demo",
                "url": image_url
            },
            timeout=10
        )
        data = r.json()
        nudity = data.get("nudity", {}).get("raw", 0)
        weapon = data.get("weapon", 0)
        return nudity > 0.5 or weapon > 0.4
    except:
        return False

async def handle_media(update: Update, context):
    msg = update.message
    if not msg:
        return
    user = msg.from_user.first_name

    # تحديد نوع المحتوى
    if msg.photo:
        file_id = msg.photo[-1].file_id
        print(f"📸 Photo from {user}")
    elif msg.sticker:
        file_id = msg.sticker.file_id
        print(f"🎴 Sticker from {user}")
    elif msg.video:
        file_id = msg.video.file_id
        print(f"🎥 Video from {user}")
    elif msg.animation:
        file_id = msg.animation.file_id
        print(f"📹 GIF from {user}")
    else:
        return

    try:
        file = await context.bot.get_file(file_id)
        url = f"https://api.telegram.org/file/bot{TOKEN}/{file.file_path}"
        if is_nsfw(url):
            await msg.delete()
            await msg.reply_text(f"⛔ Inappropriate content deleted from @{user}")
            print("   🗑️ DELETED")
        else:
            print("   ✅ KEPT")
    except Exception as e:
        print(f"Error: {e}")

def main():
    app = Application.builder().token(TOKEN).build()
    # نستخدم filters.ALL ونفحص داخل الدالة نوع المحتوى
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.ANIMATION | filters.ALL, handle_media))
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()
