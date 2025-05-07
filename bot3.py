import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import yt_dlp
from dotenv import load_dotenv

# تحميل التوكن من .env
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

# دالة start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحبًا! أرسل لي رابط فيديو من YouTube أو TikTok عشان أحمله لك.")

# دالة تحميل الفيديو
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    await update.message.reply_text(f"جاري تحميل الفيديو من: {url}")

    ydl_opts = {
        'outtmpl': '%(title)s.%(ext)s',
        'format': 'bestvideo+bestaudio/best',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
        
        # إرسال الملف بعد التحميل
        with open(file_path, 'rb') as video:
            await update.message.reply_video(video)
        
        # حذف الملف بعد الإرسال
        os.remove(file_path)

    except Exception as e:
        await update.message.reply_text(f"حدث خطأ أثناء التحميل: {e}")

# تشغيل البوت
def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    application.run_polling()

if __name__ == '__main__':
    main()
