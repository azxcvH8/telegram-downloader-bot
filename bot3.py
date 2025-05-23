import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import yt_dlp
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# تحميل التوكن من ملف .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# تسجيل الأحداث
logging.basicConfig(level=logging.INFO)

# إعداد Flask عشان السيرفر يشتغل
app = Flask(__name__)
@app.route('/')
def home():
    return "البوت شغال تمام"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# بيانات البوت
user_count = set()
download_count = 0
cache = {}

# أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("حيّاك! عطـني رابطك وخلّي التحميل عليّ.\n\nنظام VIP: قريبًا")

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
        await query.message.reply_text("ما لقيت رابط! أرسل الرابط من جديد.")
        return

    if query.data == "video":
        await download_and_send(update, context, url, "video")
    elif query.data == "audio":
        await download_and_send(update, context, url, "audio")
    elif query.data == "high":
        await download_and_send(update, context, url, "high")

# التعامل مع الرسائل
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global user_count
    user_id = update.effective_user.id
    user_count.add(user_id)

    text = update.message.text.strip()
    url = text.split()[0]

    # فلتر السبام
    if any(x in text.lower() for x in ["vpn", "telgram bot", "артур", "начать пробный", "🔒"]):
        return

    if url.startswith("http"):
        context.user_data['last_url'] = url

        if "tiktok.com/" in url and "/photo/" in url:
            await update.message.reply_text("جاري تحميل الصورة من TikTok...")
            try:
                file_path = await download_tiktok_photo(url)
                with open(file_path, 'rb') as f:
                    await update.message.reply_photo(f)
                return
            except Exception as e:
                await update.message.reply_text(f"صار فيه مشكلة:\n\n{e}")
                return

        await update.message.reply_text(
            "وش تبي أسوي بالرابط؟",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("تحميل كفيديو", callback_data="video")],
                [InlineKeyboardButton("تحميل كموسيقى", callback_data="audio")],
                [InlineKeyboardButton("جودة عالية", callback_data="high")],
            ])
        )
    else:
        await update.message.reply_text("أرسل رابط تحميل من TikTok، يوتيوب، أو غيره.")

# تحميل الصور من TikTok
async def download_tiktok_photo(url: str) -> str:
    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'format': 'bestaudio/best',
        'skip_download': True,
        'noplaylist': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if "images" in info:
            image_url = info["images"][0]["url"]
            file_name = f"downloads/{info['id']}.jpg"
            os.system(f"wget \"{image_url}\" -O \"{file_name}\"")
            return file_name
        raise Exception("ما قدرنا نلقط الصورة.")

# التحميل والإرسال
async def download_and_send(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str, mode: str):
    global download_count
    await update.callback_query.message.reply_text("أجهز لك الرابط، خلك قريب...")

    if url in cache:
        with open(cache[url], 'rb') as f:
            await update.callback_query.message.reply_document(f)
        return

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

        if os.path.getsize(file_path) > 45 * 1024 * 1024:
            await update.callback_query.message.reply_text("الفيديو كبير شوي، بجرب أضغطه...")
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

# تشغيل البوت
def main():
    if not os.path.isdir('downloads'):
        os.makedirs('downloads')

    Thread(target=run_flask).start()
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
