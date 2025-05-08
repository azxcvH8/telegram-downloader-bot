# اضافة التعديلات التالية على الكود:
from telegram.ext import Updater, Dispatcher, CommandHandler, MessageHandler, filters
from telegram import Update
import logging

# إضافة معالج الأخطاء
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

def start(update: Update, context):
    update.message.reply_text("مرحبًا! أرسل لي رابط الفيديو لتحميله.")

def download_video(update: Update, context):
    url = update.message.text.strip()
    # الكود الخاص بمعالجة تحميل الفيديو هنا
    update.message.reply_text("جاري تحميل الفيديو...")

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # إضافة معالجات الأوامر
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    # تحديد webhook
    application.run_webhook(listen="0.0.0.0", port=8080, url_path=BOT_TOKEN)
    
if __name__ == '__main__':
    main()
