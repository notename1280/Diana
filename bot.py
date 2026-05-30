import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TELEGRAM_TOKEN = "8456952048:AAF1p2qe3JwH7j8sClYqs1KARj-hv2BhMUM"
GEMINI_API_KEY = "AQ.Ab8RN6Lk67lQfQ73I6pkC9dyNKg0faxAsqAMVwNtOEf_B5iMlw"

ai_client = genai.Client(api_key=GEMINI_API_KEY)
user_chats = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    # إنشاء جلسة دردشة جديدة مع الـ System Instruction
    user_chats[user_id] = ai_client.chats.create(
        model="gemini-2.5-flash",
        config={
            'system_instruction': (
                "أنت الآن ذكاء اصطناعي مساعد اسمك 'مساعد محمد الرقمي'. "
                "يجب أن تتحدث دائماً باللهجة العراقية وبأسلوب صديق مقرب وذكي. "
                "تذكر دائماً أنك تتحدث مع محمد، وساعده في البرمجة والدراسة وأي شيء يحتاجه."
            )
        }
    )
    await update.message.reply_text("هلو محمد! أنا المساعد الذكي الخاص بك. البوت تم تحديثه وصار يتذكر الكلام، دزلي أي شي!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # إذا لم تكن هناك جلسة مستخدم، يتم إنشاؤها فوراً
    if user_id not in user_chats:
        user_chats[user_id] = ai_client.chats.create(
            model="gemini-2.5-flash",
            config={
                'system_instruction': (
                    "أنت الآن ذكاء اصطناعي مساعد اسمك 'مساعد محمد الرقمي'. "
                    "يجب أن تتحدث دائماً باللهجة العراقية وبأسلوب صديق مقرب وذكي. "
                    "تذكر دائماً أنك تتحدث مع محمد، وساعده في البرمجة والدراسة وأي شيء يحتاجه."
                )
            }
        )
    
    try:
        # إرسال الرسالة للمحادثة المستمرة (تحفظ الذاكرة تلقائياً)
        response = user_chats[user_id].send_message(user_text)
        await update.message.reply_text(response.text)
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("صارت مشكلة، تأكد من تشغيل السكربت أو الـ API Key.")

def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("البوت شغال حالياً ومستعد لاستقبال الرسائل...")
    application.run_polling()

if __name__ == '__main__':
    main()