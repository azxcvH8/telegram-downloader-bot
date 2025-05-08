import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import yt_dlp

# تحميل التوكن من البيئة
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

# إنشاء مجلد downloads لو ما كان موجود أو إذا كان خطأ
if not os.path.isdir('downloads'):
    os.makedirs('downloads')

async def start(update: Update, context):
    await update.message.reply_text("مرحبًا! أنا بوت التحميل. أرسل لي رابط الفيديو لتحميله.")

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
    application = Application.builder().token(BOT_TOKEN).build()

    # إضافة معالج أمر start
    application.add_handler(CommandHandler("start", start))

    # إضافة معالج للرسائل
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    # تحديد المنفذ (للتأكد من أنه يعمل في بيئة Render أو بيئة مشابهة)
    port = os.getenv("PORT", 8080)

    # بدء البوت مع تحديد المنفذ
    application.run_polling(port=port)

if __name__ == '__main__':
    main()
