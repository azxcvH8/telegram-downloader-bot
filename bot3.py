import os
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
    # نستخدم البورت اللي يعطينا إياه Render أو نرجع لـ 10000 إذا ما لقيناه
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# إنشاء مجلد التنزيلات لو ما كان موجود
if not os.path.isdir('downloads'):
    os.makedirs('downloads')

# أمر /start
async def start(update: Update, context):
    await update.message.reply_text("مرحبًا! أنا بوت التحميل. أرسل لي رابط الفيديو لتحميله.")

# تحميل الفيديوهات
async def download_video(update: Update, context):
    url = update.message.text.strip()
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
    # تشغيل Flask في Thread منفصل عشان ما يوقف البوت
    Thread(target=run_flask).start()

    # إعداد بوت التليجرام
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    application.run_polling()

if __name__ == '__main__':
    main()
