import os
import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")

questions = {
    "math": [
        {"q": "২০০ এর ২৫% কত?", "options": ["২৫", "৫০", "৭৫", "১০০"], "answer": "৫০"}
    ],
    "english": [
        {"q": "Synonym of Happy?", "options": ["Sad", "Joyful", "Angry", "Tired"], "answer": "Joyful"}
    ]
}

user_scores = {}
user_q = {}
user_subject = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📚 কুইজ শুরু করুন", callback_data="start")],
        [InlineKeyboardButton("📊 আমার র‍্যাংক", callback_data="rank")]
    ]
    await update.message.reply_text("স্বাগতম SSC MCQ বটে 🚀", reply_markup=InlineKeyboardMarkup(keyboard))

async def menu(update, context):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("📐 গণিত", callback_data="math")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="english")]
    ]
    await query.edit_message_text("বিষয় নির্বাচন করুন:", reply_markup=InlineKeyboardMarkup(keyboard))

async def send_q(query, user_id, subject):
    q = random.choice(questions[subject])
    user_q[user_id] = q
    user_subject[user_id] = subject

    buttons = [[InlineKeyboardButton(opt, callback_data=f"ans|{opt}")] for opt in q["options"]]
    await query.edit_message_text(q["q"], reply_markup=InlineKeyboardMarkup(buttons))

async def answer(update, context):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    selected = query.data.split("|")[1]
    correct = user_q[user_id]["answer"]

    if selected == correct:
        user_scores[user_id] = user_scores.get(user_id, 0) + 1
        msg = "✅ সঠিক!"
    else:
        msg = f"❌ ভুল! সঠিক: {correct}"

    keyboard = [[InlineKeyboardButton("➡️ পরবর্তী প্রশ্ন", callback_data="next")]]
    await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

async def next_q(update, context):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    subject = user_subject[user_id]
    await send_q(query, user_id, subject)

async def rank(update, context):
    query = update.callback_query
    await query.answer()

    sorted_users = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)
    user_id = query.from_user.id

    if user_id in user_scores:
        rank = [u[0] for u in sorted_users].index(user_id) + 1
    else:
        rank = "N/A"

    score = user_scores.get(user_id, 0)

    await query.edit_message_text(f"🏆 স্কোর: {score}\n🇧🇩 র‍্যাংক: #{rank}")

async def handler(update, context):
    data = update.callback_query.data

    if data == "start":
        await menu(update, context)
    elif data in ["math", "english"]:
        await send_q(update.callback_query, update.callback_query.from_user.id, data)
    elif data.startswith("ans"):
        await answer(update, context)
    elif data == "next":
        await next_q(update, context)
    elif data == "rank":
        await rank(update, context)

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(handler))

print("Bot is running...")
app.run_polling()
