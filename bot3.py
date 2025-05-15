import os
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import yt_dlp
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

# تأكد من وجود مجلد downloads
if not os.path.isdir('downloads'):
    os.makedirs('downloads')

# تحديد نوع المنصة من الرابط
def get_platform(url):
    if "tiktok.com" in url:
        return "TikTok"
    elif "youtube.com" in url or "youtu.be" in url:
        return "YouTube"
    elif "twitter.com" in url or "x.com" in url:
        return "Twitter"
    elif "instagram.com" in url:
        return "Instagram"
    else:
        return "رابط غير معروف"

# أمر /start
async def start(update: Update, context):
    await update.message.reply_text(
        "مرحبًا! أنا بوت تحميل الفيديوهات.\n"
        "أرسل لي رابط من YouTube، TikTok، Twitter أو Instagram لتحميله.\n"
        "استخدم /help لمزيد من المعلومات."
    )

# أمر /help
async def help_command(update: Update, context):
    await update.message.reply_text(
        "البوت يدعم حالياً:\n"
        "- YouTube (بعض المقاطع تحتاج تسجيل دخول)\n"
        "- TikTok\n"
        "- Twitter / X\n"
        "- Instagram\n\n"
        "أرسل الرابط فقط، والبوت يحمله لك."
    )

# تحميل الفيديو
async def download_video(update: Update, context):
    url = update.message.text.strip()
    platform = get_platform(url)

    await update.message.reply_text(f"جاري تحميل الفيديو من {platform}...")

    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'noplaylist': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_path = ydl.prepare_filename(info_dict)

        # رفع كملف document عشان مقاطع كثيرة تكون كبيرة
        with open(video_path, 'rb') as video_file:
            await update.message.reply_document(video_file)
    except Exception as e:
        await update.message.reply_text(f"حدث خطأ أثناء التحميل:\n{e}")

# تشغيل البوت
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    app.run_polling()

if __name__ == '__main__':
    main()
