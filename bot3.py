import logging
import os
import yt_dlp
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

# إعدادات
TOKEN = "توكن_البوت_حقك"
logging.basicConfig(level=logging.INFO)

# دالة التنزيل
def download_video(url, format_code='mp4'):
    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'video.%(ext)s',
        }

        if format_code == 'audio':
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': 'audio.%(ext)s',
            })
        elif format_code == 'high':
            ydl_opts['format'] = 'bestvideo+bestaudio/best'

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if format_code == 'audio':
                filename = filename.rsplit('.', 1)[0] + '.mp3'
            return filename
    except Exception as e:
        return f"error: {e}"

# رسالة البدء
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("هلا بك! أرسل رابط الفيديو من أي منصة.")

# استقبال الرسائل (الروابط)
async def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    if not text.startswith("http"):
        await update.message.reply_text("أرسل رابط صحيح!")
        return

    # نحفظ الرابط في user_data
    context.user_data['last_url'] = text

    await update.message.reply_text(
        "وش تبي أسوي بالرابط؟",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("تحميل كفيديو", callback_data="video")],
            [InlineKeyboardButton("تحميل كموسيقى", callback_data="audio")],
            [InlineKeyboardButton("جودة عالية", callback_data="high")],
        ])
    )

# التعامل مع الأزرار
async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    # نرجع للرابط المحفوظ
    url = context.user_data.get('last_url')
    if not url:
        await query.edit_message_text("ما حصلت الرابط. أرسل الرابط من جديد.")
        return

    choice = query.data
    format_code = 'mp4'
    if choice == 'audio':
        format_code = 'audio'
    elif choice == 'high':
        format_code = 'high'

    await query.edit_message_text("جاري التحميل...")

    result = download_video(url, format_code=format_code)

    if isinstance(result, str) and result.startswith("error:"):
        await query.message.reply_text(f"صار فيه خطأ أثناء التحميل:\n\n{result}")
    else:
        with open(result, 'rb') as f:
            if format_code == 'audio':
                await query.message.reply_audio(f)
            else:
                await query.message.reply_video(f)
        os.remove(result)

# تشغيل البوت
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("البوت شغال...")
    app.run_polling()

if __name__ == "__main__":
    main()
