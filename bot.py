from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import requests
from googletrans import Translator

# تابع دریافت اخبار و ترجمه به فارسی
def get_news():
    url = "https://newsapi.org/v2/everything?q=gold+dollar+economy+iran&language=en&sortBy=publishedAt&apiKey=27284966a77a4619a5c89846514cb284"
    response = requests.get(url)
    articles = response.json().get("articles", [])[:5]
    
    translator = Translator()
    news_list = []

    for a in articles:
        english_text = f"{a['title']} - {a['source']['name']}"
        translated = translator.translate(english_text, src='en', dest='fa')
        news_list.append(translated.text)

    return "\n".join(news_list)

# تابع تحلیل اخبار ترجمه‌شده
def analyze_news(news_text):
    keywords_buy = [
        "تورم", "افزایش نرخ بهره", "تحریم", "بحران", "درگیری",
        "جنگ", "تنش", "افزایش قیمت نفت", "افزایش ارزش دلار", "افزایش نرخ فدرال", "کاهش ارزش پول ملی"
    ]
    keywords_sell = [
        "صلح", "توافق", "مذاکره", "قرارداد", "کاهش نرخ بهره",
        "کاهش ارزش دلار", "کاهش قیمت نفت", "رشد اقتصادی", "ثبات"
    ]

    for word in keywords_buy:
        if word in news_text:
            return "📈 احتمال افزایش قیمت طلا و دلار وجود دارد. سیگنال خرید."

    for word in keywords_sell:
        if word in news_text:
            return "📉 احتمال کاهش قیمت طلا و دلار وجود دارد. سیگنال فروش."

    return "ℹ️ خبر خاصی مشاهده نشد. سیگنالی صادر نمی‌شود."


# /start: نمایش منوی کلیددار
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("📊 آنالیز اخبار")],
        [KeyboardButton("💹 دریافت سیگنال")],
        [KeyboardButton("🔄 به‌روزرسانی اخبار")],
        [KeyboardButton("ℹ️ راهنما")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "سلام! من ربات تحلیل‌گر بازار طلا و دلار هستم.\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=reply_markup
    )

# کنترل عملکرد کلیدها
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📊 آنالیز اخبار":
        news = get_news()
        signal = analyze_news(news)
        await update.message.reply_text(f"📰 اخبار منتخب (ترجمه‌شده):\n{news}\n\n🔍 تحلیل:\n{signal}")
    
    elif text == "💹 دریافت سیگنال":
        news = get_news()
        signal = analyze_news(news)
        await update.message.reply_text(f"📈 سیگنال نهایی:\n{signal}")
    
    elif text == "🔄 به‌روزرسانی اخبار":
        news = get_news()
        await update.message.reply_text(f"📥 جدیدترین اخبار (ترجمه‌شده):\n{news}")
    
    elif text == "ℹ️ راهنما":
        await update.message.reply_text("📘 راهنمای استفاده:\n\n"
            "- برای تحلیل بازار روی '📊 آنالیز اخبار' بزن.\n"
            "- برای دریافت فقط سیگنال سریع، روی '💹 دریافت سیگنال' بزن.\n"
            "- برای مشاهده فقط اخبار ترجمه‌شده، روی '🔄 به‌روزرسانی اخبار' بزن.\n"
            "- اگر سوالی داشتی، دوباره /start رو بزن تا منو نمایش داده بشه.")

    else:
        await update.message.reply_text("⛔ دستور نامعتبر است. لطفاً فقط از دکمه‌ها استفاده کن.")

# اجرای ربات
app = ApplicationBuilder().token("7721073253:AAGq1z2wcdI68SdW06a3xo88dMOGycmcJoY").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))
app.run_polling()
