import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import yt_dlp
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# تحميل متغيرات البيئة
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

# إعداد تسجيل الدخول
logging.basicConfig(level=logging.INFO)

# إعداد تطبيق Flask
app = Flask(__name__)
@app.route('/')
def home():
    return "البوت شغال تمام!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# إعداد مجلد التحميل
if not os.path.exists('downloads'):
    os.makedirs('downloads')

# إحصائيات بسيطة
user_count = set()
download_count = 0

# كاش مؤقت
cache = {}

# بدء البوت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("حيّاك! عطِـني رابطك وخلّي التحميل علي.\n\nنظام VIP: قريبًا")

# إحصائيات
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"عدد المستخدمين: {len(user_count)}\nعدد التحميلات: {download_count}\nنظام VIP: قريبًا"
    )

# زر التحميل
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not query.message or not query.message.text or not query.message.text.startswith("http"):
        await query.message.reply_text("ما حصلت رابط أتعامل معه.")
        return

    url = query.message.text

    if query.data == "video":
        await download_and_send(update, context, url, mode="video")
    elif query.data == "audio":
        await download_and_send(update, context, url, mode="audio")
    elif query.data == "high":
        await download_and_send(update, context, url, mode="high")

# الرد على الرسائل
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global user_count
    user_id = update.effective_user.id
    user_count.add(user_id)

    if not update.message or not update.message.text:
        return

    url = update.message.text.strip()

    if not url.startswith("http"):
        await update.message.reply_text("الرابط هذا شكله خربان أو مو مدعوم حاليًا.")
        return

    # صورة TikTok
    if "tiktok.com/" in url and "/photo/" in url:
        await update.message.reply_text("جاري تحميل الصورة...")
        await download_and_send(update, context, url, mode="photo")
        return

    # فيديوهات
    keyboard = [
        [InlineKeyboardButton("تحميل فيديو", callback_data="video")],
        [InlineKeyboardButton("تحميل موسيقى", callback_data="audio")],
        [InlineKeyboardButton("جودة عالية", callback_data="high")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("وش تبي أسوي بالرابط؟", reply_markup=reply_markup)

# تحميل الملف
async def download_and_send(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str, mode="video"):
    global download_count

    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True,
        'nocheckcertificate': True,
    }

    if mode == "audio":
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    elif mode == "high":
        ydl_opts['format'] = 'bestvideo+bestaudio/best'
    elif mode == "photo":
        ydl_opts['format'] = 'best'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            if mode == "audio":
                file_path = os.path.splitext(file_path)[0] + ".mp3"

        download_count += 1
        if mode == "audio":
            await update.effective_message.reply_audio(audio=open(file_path, 'rb'))
        elif file_path.endswith(".jpg") or file_path.endswith(".png") or mode == "photo":
            await update.effective_message.reply_photo(photo=open(file_path, 'rb'))
        else:
            await update.effective_message.reply_document(document=open(file_path, 'rb'))

        os.remove(file_path)
    except Exception as e:
        await update.effective_message.reply_text(f"صار فيه خطأ أثناء التحميل:\n\n{e}")

# تشغيل التطبيق
def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # تشغيل Flask في ثريد منفصل
    Thread(target=run_flask).start()

    # تشغيل البوت
    application.run_polling()

main()
