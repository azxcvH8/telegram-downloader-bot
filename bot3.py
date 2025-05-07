import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import yt_dlp

# تحميل التوكن من البيئة
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

async def start(update: Update, context):
    await update.message.reply_text("مرحبًا! أنا بوت التحميل. أرسل لي رابط الفيديو لتحميله.")

async def download_video(update: Update, context):
    url = update.message.text.strip()  # ناخذ الرابط فقط ونشيل المسافات الزايدة
    await update.message.reply_text(f"جاري تحميل الفيديو...")

    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',  # مجلد التخزين
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_path = ydl.prepare_filename(info_dict)
        
        # نرسل الملف نفسه
        with open(video_path, 'rb') as video_file:
            await update.message.reply_video(video_file)
    except Exception as e:
        await update.message.reply_text(f"حدث خطأ أثناء التحميل: {e}")

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    application.run_polling()

if __name__ == '__main__':
    main()
