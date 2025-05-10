from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from deep_translator import GoogleTranslator
import requests

# 📰 دریافت اخبار جهانی
def get_global_news():
    news_list = []

    # NewsAPI
    try:
        url = "https://newsapi.org/v2/everything?q=gold+dollar+oil+crypto+war&language=en&sortBy=publishedAt&apiKey=27284966a77a4619a5c89846514cb284"
        articles = requests.get(url).json().get("articles", [])[:3]
        for a in articles:
            news_list.append(a["title"])
    except:
        pass

    # GNews
    try:
        url = "https://gnews.io/api/v4/search?q=gold+dollar+crypto+war+oil&lang=en&token=cc588426fdda5e76dd8e4f8f7706616e"
        articles = requests.get(url).json().get("articles", [])[:3]
        for a in articles:
            news_list.append(a["title"])
    except:
        pass

    # Mediastack
    try:
        url = "http://api.mediastack.com/v1/news?access_key=c50464aae1764f79a272dfaa41cf478f&keywords=dollar,gold,crypto,war&languages=en"
        articles = requests.get(url).json().get("data", [])[:3]
        for a in articles:
            news_list.append(a["title"])
    except:
        pass

    return news_list

# 📰 دریافت اخبار ایران
def get_iran_news():
    news_list = []
    try:
        url = "https://newsdata.io/api/1/news?apikey=api_live_OQyfGEsKxBWbMbIv2g5VBZXIxlKcQTMiI5Va5tccJ2&country=ir&language=fa&category=business,politics"
        articles = requests.get(url).json().get("results", [])[:5]
        for a in articles:
            news_list.append(a["title"])
    except:
        pass
    return news_list

# 🔄 ترجمه اخبار
def translate_news(news_list):
    translated = []
    for item in news_list:
        try:
            translated.append(GoogleTranslator(source='auto', target='fa').translate(item))
        except:
            translated.append(item)
    return translated

# 📈 تحلیل اخبار و تولید سیگنال
def analyze_news(news_texts):
    buy_keywords = ["تحریم", "افزایش نرخ بهره", "بحران", "جنگ", "تورم", "تنش", "افزایش قیمت نفت", "کاهش ارزش پول"]
    sell_keywords = ["توافق", "صلح", "کاهش نرخ بهره", "ثبات", "رشد اقتصادی"]

    for news in news_texts:
        for word in buy_keywords:
            if word in news:
                return "📈 سیگنال خرید: احتمال افزایش قیمت طلا، دلار یا رمزارزها وجود دارد."
        for word in sell_keywords:
            if word in news:
                return "📉 سیگنال فروش: احتمال کاهش قیمت طلا، دلار یا رمزارزها وجود دارد."
    return "ℹ️ سیگنالی یافت نشد."

# 🎛 منوی دکمه‌ها
def main_menu():
    keyboard = [
        [KeyboardButton("🌍 تحلیل اخبار جهانی")],
        [KeyboardButton("🇮🇷 تحلیل اخبار ایران")],
        [KeyboardButton("🌐 تحلیل ترکیبی")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! به ربات تحلیل بازار طلا، دلار و رمزارز خوش آمدید.", reply_markup=main_menu())

# 🎯 واکنش به دکمه‌ها
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text

    if msg == "🌍 تحلیل اخبار جهانی":
        news = get_global_news()
        translated = translate_news(news)
        signal = analyze_news(translated)
        await update.message.reply_text("📰 اخبار جهانی:\n" + "\n".join(translated) + "\n\n🔍 " + signal)

    elif msg == "🇮🇷 تحلیل اخبار ایران":
        news = get_iran_news()
        signal = analyze_news(news)
        await update.message.reply_text("🗞️ اخبار ایران:\n" + "\n".join(news) + "\n\n🔍 " + signal)

    elif msg == "🌐 تحلیل ترکیبی":
        news_global = get_global_news()
        news_iran = get_iran_news()
        translated = translate_news(news_global)
        combined = news_iran + translated
        signal = analyze_news(combined)
        await update.message.reply_text("📡 تحلیل ترکیبی:\n" + "\n".join(combined) + "\n\n🔍 " + signal)

    else:
        await update.message.reply_text("دستور نامعتبر است. لطفاً از منوی دکمه‌ها استفاده کنید.")

# اجرای ربات
app = ApplicationBuilder().token("7721073253:AAGq1z2wcdI68SdW06a3xo88dMOGycmcJoY").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, handle_buttons))
app.run_polling()
