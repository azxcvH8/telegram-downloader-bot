import os
import re
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import yt_dlp
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

app = Flask(__name__)

@app.route('/')
def home():
    return "بوت LoadKing شغال تمام"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if not os.path.isdir('downloads'):
    os.makedirs('downloads')

async def start(update: Update, context):
    await update.message.reply_text("مرحبًا! أرسل لي رابط فيديو أو صورة تيك توك لتحميله.")

# دالة لتحميل صورة من رابط تيك توك وحفظها ثم إرسالها للمستخدم
async def download_tiktok_photo(update: Update, url: str):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
    except Exception as e:
        await update.message.reply_text(f"خطأ في تحميل رابط الصورة: {e}")
        return

    # نحاول نطلع رابط الصورة من صفحة التيك توك
    match = re.search(r'"displayImage":"([^"]+)"', res.text)
    if not match:
        match = re.search(r'"cover":"([^"]+)"', res.text)

    if not match:
        await update.message.reply_text("ما قدرت ألقى رابط الصورة.")
        return

    image_url = match.group(1).replace('\\u0026', '&')
    image_name = image_url.split("/")[-1].split("?")[0]

    # ننزل الصورة ونحفظها في مجلد downloads
    try:
        img_data = requests.get(image_url, headers=headers).content
        file_path = os.path.join('downloads', image_name)
        with open(file_path, 'wb') as f:
            f.write(img_data)
    except Exception as e:
        await update.message.reply_text(f"خطأ أثناء تنزيل الصورة: {e}")
        return

    # نرسل الصورة للمستخدم من الملف المحفوظ
    with open(file_path, 'rb') as photo_file:
        await update.message.reply_photo(photo_file)

async def download_video(update: Update, context):
    url = update.message.text.strip()

    # إذا الرابط من تيك توك وصورة
    if "tiktok.com" in url and "photo" in url:
        await download_tiktok_photo(update, url)
        return

    # تحميل الفيديوهات العادية بـ yt-dlp
    await update.message.reply_text("جاري تحميل الفيديو...")
    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_path = ydl.prepare_filename(info_dict)

        with open(video_path, 'rb') as video_file:
            await update.message.reply_video(video_file)
    except Exception as e:
        await update.message.reply_text(f"حدث خطأ أثناء التحميل: {e}")

def main():
    Thread(target=run_flask).start()

    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    application.run_polling()

if __name__ == '__main__':
    main()
