import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai
import asyncio
import os

logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8456952048:AAF1p2qe3JwH7j8sClYqs1KARj-hv2BhMUM")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6LXAht74_gF4JQTckSDzYWVWub-t4SCUGmRzkhn8oq_pA")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "https://diana-production-649b.up.railway.app)

ai_client = genai.Client(api_key=GEMINI_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("هلو! البوت شغال وجاهز أساعدك 🤖")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        response = ai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_text,
            config={
                'system_instruction': (
                    "أنت ذكاء اصطناعي مساعد اسمك 'مساعد محمد الرقمي'. "
                    "تحدث دائماً باللهجة العراقية وبأسلوب صديق مقرب وذكي. "
                    "ساعد محمد في البرمجة والدراسة وأي شيء يحتاجه."
                )
            }
        )
        await update.message.reply_text(response.text)
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("كو مشكلة بالاتصال، حاول مرة ثانية.")

# إنشاء event loop ثابت
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

application = Application.builder().token(TELEGRAM_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

loop.run_until_complete(application.initialize())

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running! ✅"

@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def webhook():
    data = request.get_json()
    update = Update.de_json(data, application.bot)
    loop.run_until_complete(application.process_update(update))
    return 'ok'

@app.route('/set_webhook')
def set_webhook():
    url = f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}"
    loop.run_until_complete(application.bot.set_webhook(url=url))
    return f"✅ Webhook set to: {url}"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
