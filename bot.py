import logging
import requests
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio
import os

logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8456952048:AAF1p2qe3JwH7j8sClYqs1KARj-hv2BhMUM")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "https://diana-production-649b.up.railway.app")

CF_TOKEN = os.environ.get("CF_TOKEN", "cfut_hGSoxbF1VyJNIXPFwu86SZpQeOdc5BBGSZ1LTA1h87b57103")
CF_ACCOUNT = os.environ.get("CF_ACCOUNT", "5a9bc64e37f76de2dc68eb7bcfa37411")
CF_URL = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT}/ai/run/@cf/meta/llama-3.3-70b-instruct-fp8-fast"

def ask_ai(user_text):
    headers = {"Authorization": f"Bearer {CF_TOKEN}"}
    payload = {
        "messages": [
            {
                "role": "system",
                "content": (
          "أنتِ 'ديانا'، الصديقة المقربة والذكية لمحمد. تتحدثين حصراً باللهجة العراقية الدارجة (بدون أي كلمات أجنبية أو فصحى). أسلوبك كيوت، عفوي، وبشري 100%؛ تستخدمين مفردات عراقية لطيفة, شخصيتك ذكية لكنها متواضعة وبسيطة، تتجنبين التكرار، وتكونين مباشرة وواضحة جداً في إجاباتك. لا تتحدثين بصيغة المذكر أبداً ولا تستخدمين أي كلمات غريبة؛ أنتِ فقط ديانا، صديقة محمد الرقمية التي تهتم به وتساعده بكل لطف."
            },
            {"role": "user", "content": user_text}
        ]
    }
    response = requests.post(CF_URL, headers=headers, json=payload)
    logging.info(f"CF Response: {response.text}")
    result = response.json()
    
    # محاولة قراءة الرد بأكثر من طريقة
    if result.get("result"):
        return result["result"].get("response") or str(result["result"])
    elif result.get("errors"):
        logging.error(f"CF Error: {result['errors']}")
        return "كو مشكلة بالـ AI، حاول مرة ثانية."
    else:
        return str(result)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("هلو! البوت شغال وجاهز أساعدك 🤖")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        reply = ask_ai(user_text)
        await update.message.reply_text(reply)
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("كو مشكلة بالاتصال، حاول مرة ثانية.")

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
