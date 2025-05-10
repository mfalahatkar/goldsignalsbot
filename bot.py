from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import requests

# دریافت اخبار اقتصادی
def get_news():
    url = "https://newsapi.org/v2/everything?q=gold+dollar+economy+iran&language=en&sortBy=publishedAt&apiKey=27284966a77a4619a5c89846514cb284"
    response = requests.get(url)
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
            return "📈 احتمال افزایش قیمت طلا و دلار وجود دارد. سیگنال خرید."

    for word in keywords_sell:
        if word in news_text:
            return "📉 احتمال کاهش قیمت طلا و دلار وجود دارد. سیگنال فروش."

    return "ℹ️ خبر خاصی مشاهده نشد. سیگنالی صادر نمی‌شود."


# فرمان /start با کیبورد دکمه‌ای
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("📊 آنالیز اخبار")],
        [KeyboardButton("💹 دریافت سیگنال")],
        [KeyboardButton("🔄 به‌روزرسانی اخبار")],
        [KeyboardButton("ℹ️ راهنما")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "سلام! من ربات تحلیلگر بازار طلا و دلار هستم.\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=reply_markup
    )

# واکنش به دکمه‌های کیبورد
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📊 آنالیز اخبار":
        news = get_news()
        signal = analyze_news(news.lower())
        await update.message.reply_text(f"📰 اخبار منتخب:\n{news}\n\n🔍 تحلیل:\n{signal}")
    
    elif text == "💹 دریافت سیگنال":
        news = get_news()
        signal = analyze_news(news.lower())
        await update.message.reply_text(f"📈 سیگنال نهایی:\n{signal}")
    
    elif text == "🔄 به‌روزرسانی اخبار":
        news = get_news()
        await update.message.reply_text(f"📥 جدیدترین اخبار:\n{news}")
    
    elif text == "ℹ️ راهنما":
        await update.message.reply_text("📘 برای تحلیل بازار فقط کافیست یکی از دکمه‌های پایین را فشار دهید.\nهر بار روی 'آنالیز اخبار' یا 'دریافت سیگنال' بزنید تا جدیدترین تحلیل به شما داده شود.")
    
    else:
        await update.message.reply_text("⛔ دستور نامعتبر است. لطفاً فقط از دکمه‌ها استفاده کنید.")

# اجرای ربات
app = ApplicationBuilder().token("7721073253:AAGq1z2wcdI68SdW06a3xo88dMOGycmcJoY").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(handle_buttons))  # برای دکمه‌های اینلاین اگر در آینده اضافه شد
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))

app.run_polling()
