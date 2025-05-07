import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import yt_dlp

# تحميل التوكن من البيئة
from dotenv import load_dotenv

load_dotenv()  # تحميل محتويات .env

# الحصول على التوكن
BOT_TOKEN = os.getenv('BOT_TOKEN')

# إعداد البوت
async def start(update: Update, context):
    await update.message.reply_text("مرحبًا! أنا بوت التحميل. أرسل لي رابط الفيديو لتحميله.")

# دالة لتحميل الفيديو
async def download_video(update: Update, context):
    url = update.message.text
    await update.message.reply_text(f"جاري تحميل الفيديو من: {url}")

    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',  # حفظ الفيديو في مجلد 'downloads'
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        video_url = info_dict.get('url', None)

    # إرسال الفيديو بعد تحميله
    await update.message.reply_video(video_url)

def main():
    # إعداد التطبيق
    application = Application.builder().token(BOT_TOKEN).build()

    # إضافة أمر start
    application.add_handler(CommandHandler("start", start))

    # إضافة معالجة للرسائل
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    # تحديد المنفذ (للتأكد من أنه يعمل في بيئة Render)
    port = os.getenv("PORT", 8080)

    # بدء البوت
    application.run_polling(port=port)

if __name__ == '__main__':
    main()
