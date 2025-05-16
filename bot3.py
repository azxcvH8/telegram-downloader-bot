import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import yt_dlp
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# تحميل المتغيرات من ملف .env
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

# إنشاء تطبيق Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "بوت LoadKing شغال تمام"

# دالة لتشغيل Flask في Thread منفصل
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# إنشاء مجلد التنزيلات لو ما كان موجود
if not os.path.isdir('downloads'):
    os.makedirs('downloads')

# أمر /start
async def start(update: Update, context):
    await update.message.reply_text("مرحبًا! أنا بوت التحميل. أرسل لي رابط الفيديو أو الصورة.")

# تحميل الفيديو أو الصورة
async def download_video(update: Update, context):
    url = update.message.text.strip()
    await update.message.reply_text("جاري التحميل...")

    try:
        if "tiktok.com" in url and "/photo/" in url:
            # محاولة استخراج صورة TikTok
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            image_url = None

            # نحاول نلقط رابط الصورة من داخل الصفحة
            for line in response.text.split('"'):
                if ".jpeg" in line or ".jpg" in line or ".png" in line:
                    if "https" in line and "webp" not in line:
                        image_url = line
                        break

            if image_url:
                img_data = requests.get(image_url).content
                image_path = 'downloads/photo.jpg'
                with open(image_path, 'wb') as handler:
                    handler.write(img_data)
                with open(image_path, 'rb') as photo:
                    await update.message.reply_photo(photo)
                return
            else:
                await update.message.reply_text("ما قدرت ألقى الصورة داخل الرابط.")
                return

        # تحميل الفيديوهات
        ydl_opts = {
            'outtmpl': 'downloads/%(title)s.%(ext)s',
        }

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
