from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
import requests

# دریافت اخبار اقتصادی
def get_news():
    url = "https://newsapi.org/v2/everything?q=gold+dollar+economy+iran&language=en&sortBy=publishedAt&apiKey=27284966a77a4619a5c89846514cb284"
    response = requests.get(url)
    
    # بررسی وضعیت درخواست
    if response.status_code != 200:
        return "مشکلی در دریافت اخبار از API به وجود آمد."
    
    articles = response.json().get("articles", [])[:5]
    news_list = [f"{a['title']} - {a['source']['name']}" for a in articles]
    return "\n".join(news_list)

# تحلیل ساده اخبار
def analyze_news(news_text):
    keywords_buy = [
        "inflation", "interest rate", "sanction", "crisis", "conflict",
        "war", "tension", "oil price rise", "usd rise", "fed hike", "devaluation"
    ]
    keywords_sell = [
        "peace", "agreement", "negotiation", "deal", "interest rate cut",
        "usd fall", "oil price drop", "recovery", "growth", "stability"
    ]

    for word in keywords_buy:
        if word in news_text:
            return "احتمال افزایش قیمت طلا و دلار وجود دارد. سیگنال خرید."

    for word in keywords_sell:
        if word in news_text:
            return "احتمال کاهش قیمت طلا و دلار وجود دارد. سیگنال فروش."

    return "خبر خاصی مشاهده نشد. سیگنالی صادر نمی‌شود."

# فرمان /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("آنالیز بازار طلا و دلار", callback_data='analyze')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("سلام! من ربات تحلیلگر بازار طلا و دلار هستم.\nبرای دریافت تحلیل، روی دکمه زیر کلیک کنید.", reply_markup=reply_markup)

# فرمان /analyze
async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    news = get_news()
    signal = analyze_news(news.lower())
    await update.message.reply_text(f"اخبار منتخب:\n{news}\n\nتحلیل:\n{signal}")

# اینجا برای دکمه‌هایی که کاربر کلیک می‌کنه:
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # برای پاسخ دادن به دکمه
    if query.data == 'analyze':
        news = get_news()
        signal = analyze_news(news.lower())
        await query.edit_message_text(f"اخبار منتخب:\n{news}\n\nتحلیل:\n{signal}")

# راه‌اندازی ربات
app = ApplicationBuilder().token("7721073253:AAGq1z2wcdI68SdW06a3xo88dMOGycmcJoY").build()

# افزودن هندلرها
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))  # اضافه کردن هندلر برای دکمه‌ها

# اجرای ربات
app.run_polling()
