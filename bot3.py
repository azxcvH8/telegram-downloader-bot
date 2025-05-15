import os
import threading
import http.server
import socketserver

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import yt_dlp

from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

# إنشاء مجلد downloads إذا ما كان موجود
if not os.path.exists('downloads'):
    os.makedirs('downloads')

async def start(update: Update, context):
    await update.message.reply_text("مرحبًا! أنا بوت التحميل. أرسل لي رابط الفيديو لتحميله.")

async def download_video(update: Update, context):
    url = update.message.text.strip()
    await update.message.reply_text("جاري تحميل الفيديو...")

    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_path = ydl.prepare_filename(info_dict)

        with open(video_path, 'rb') as video_file:
            await update.message.reply_document(video_file)
    except Exception as e:
        await update.message.reply_text(f"حدث خطأ أثناء التحميل: {e}")

# سيرفر وهمي لفتح منفذ يخلي Render ما يوقف الخدمة
def start_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), Handler) as httpd:
        print(f"Dummy server running on port {port}")
        httpd.serve_forever()

def main():
    # تشغيل السيرفر الوهمي في الخلفية
    threading.Thread(target=start_dummy_server, daemon=True).start()

    # تشغيل بوت التليجرام
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    application.run_polling()

if __name__ == '__main__':
    main()
