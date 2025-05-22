import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import yt_dlp
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

# إعداد الفلوج
logging.basicConfig(level=logging.INFO)

# Flask للسيرفر الخارجي
app = Flask(__name__)
@app.route('/')
def home():
    return "البوت شغّال تمام"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# إحصائيات
user_count = set()
download_count = 0

# كاش مؤقت
cache = {}

# رسالة الترحيب
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("حيّاااك! يالذيب عطِـني رابطك وخلّي التحميل على\n\nنظام VIP: قريبًا")

# أمر /stats
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"عدد المستخدمين: {len(user_count)}\nعدد التحميلات: {download_count}\nنظام VIP: قريبًا"
    )

# أزرار التحميل
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    url = context.user_data.get('last_url')
    if not url:
        await query.message.reply_text("ما لقيت رابط أحمّله! أرسل الرابط من جديد.")
        return

    if query.data == "video":
        await download_and_send(update, context, url, mode="video")
    elif query.data == "audio":
        await download_and_send(update, context, url, mode="audio")
    elif query.data == "high":
        await download_and_send(update, context, url, mode="high")

# التعامل مع الروابط
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global user_count
    user_id = update.effective_user.id
    user_count.add(user_id)

    url = update.message.text.strip().split()[0]

    if not url.startswith("http"):
        await update.message.reply_text("الرابط هذا شكله خربان أو مو مدعوم حاليًا. تأكد منه أو جرب غيره")
        return

    # حفظ الرابط لاستخدامه مع الأزرار
    context.user_data['last_url'] = url

    # صور TikTok
    if "tiktok.com/" in url and "/photo/" in url:
        await update.message.reply_text("دعم تحميل صور TikTok بيكون ضمن نظام VIP: قريبًا")
        return

    await update.message.reply_text(
        "وش تبي أسوي بالرابط؟",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("تحميل كفيديو", callback_data="video")],
            [InlineKeyboardButton("تحميل كموسيقى", callback_data="audio")],
            [InlineKeyboardButton("جودة عالية", callback_data="high")],
        ])
    )

# التحميل
async def download_and_send(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str, mode: str):
    global download_count

    if url in cache:
        with open(cache[url], 'rb') as f:
            await update.callback_query.message.reply_document(f)
        return

    await update.callback_query.message.reply_text("أجهز لك الرابط، خلك قريب...")

    file_format = "best"
    postprocess = []

    if mode == "audio":
        file_format = "bestaudio"
        postprocess = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    elif mode == "high":
        file_format = "bestvideo[height<=1080]+bestaudio/best"

    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'format': file_format,
        'postprocessors': postprocess,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        # ضغط الفيديو لو كبير
        if os.path.getsize(file_path) > 45 * 1024 * 1024:
            await update.callback_query.message.reply_text("الفيديو كبير شوي، بجرب أضغطه لك...")
            compressed_path = "downloads/compressed.mp4"
            os.system(f"ffmpeg -i \"{file_path}\" -vcodec libx264 -crf 28 \"{compressed_path}\"")
            file_path = compressed_path

        with open(file_path, 'rb') as f:
            await update.callback_query.message.reply_document(f)

        download_count += 1
        cache[url] = file_path

    except Exception as e:
        error_msg = str(e)
        if "status code 10235" in error_msg:
            await update.callback_query.message.reply_text("المقطع خاص، محذوف، أو يحتاج تسجيل دخول.")
        else:
            await update.callback_query.message.reply_text(f"صار فيه خطأ أثناء التحميل:\n\n{error_msg}")

# التشغيل
def main():
    Thread(target=run_flask).start()
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == "__main__":
    if not os.path.isdir('downloads'):
        os.makedirs('downloads')
    main()
