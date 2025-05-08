import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# تحميل التوكن من البيئة
from dotenv import load_dotenv

load_dotenv()  # تحميل محتويات .env

# الحصول على التوكن
BOT_TOKEN = os.getenv('BOT_TOKEN')

# إعداد البوت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحبًا! أنا بوت التحميل.")

def main():
    # إعداد التطبيق
    application = Application.builder().token(BOT_TOKEN).build()

    # إضافة أمر start
    application.add_handler(CommandHandler("start", start))

    # بدء البوت
    application.run_polling()

if __name__ == '__main__':
    main()
