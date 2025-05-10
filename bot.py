from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from deep_translator import GoogleTranslator
import requests

# === API Keys ===
NEWSAPI_KEY = "27284966a77a4619a5c89846514cb284"
GNEWS_KEY = "cc588426fdda5e76dd8e4f8f7706616e"
MEDIASTACK_KEY = "c50464aae1764f79a272dfaa41cf478f"
NEWSDATA_KEY = "api_live_OQyfGEsKxBWbMbIv2g5VBZXIxlKcQTMiI5Va5tccJ2"

# === News Fetching Functions ===
def fetch_news_newsapi():
    url = f"https://newsapi.org/v2/everything?q=gold+dollar+crypto+iran+oil+sanctions&language=en&sortBy=publishedAt&apiKey={NEWSAPI_KEY}"
    return requests.get(url).json().get("articles", [])[:5]

def fetch_news_gnews():
    url = f"https://gnews.io/api/v4/search?q=iran+dollar+gold&lang=en&token={GNEWS_KEY}"
    return requests.get(url).json().get("articles", [])[:5]

def fetch_news_mediastack():
    url = f"http://api.mediastack.com/v1/news?access_key={MEDIASTACK_KEY}&keywords=iran+dollar+gold&languages=en"
    return requests.get(url).json().get("data", [])[:5]

def fetch_news_newsdata():
    url = f"https://newsdata.io/api/1/news?apikey={NEWSDATA_KEY}&q=iran+dollar+gold&country=ir&language=fa"
    return requests.get(url).json().get("results", [])[:5]

# === Translation ===
def translate(text):
    try:
        return GoogleTranslator(source='auto', target='fa').translate(text)
    except:
        return text

# === Simple News Analyzer ===
def analyze_news(text):
    buy_signals = ["تحریم", "افزایش نرخ بهره", "تنش", "درگیری", "جنگ", "نرخ نفت", "کاهش ارزش ریال"]
    sell_signals = ["توافق", "مذاکره", "کاهش نرخ بهره", "ثبات"]

    score = 0
    for word in buy_signals:
        if word in text:
            score += 1
    for word in sell_signals:
        if word in text:
            score -= 1

    if score > 0:
        return "📈 سیگنال خرید: احتمال افزایش قیمت طلا و دلار وجود دارد."
    elif score < 0:
        return "📉 سیگنال فروش: احتمال کاهش قیمت طلا و دلار وجود دارد."
    else:
        return "ℹ️ سیگنال خاصی در اخبار مشاهده نشد."

# === Daily Prices ===
def fetch_daily_rates():
    try:
        response = requests.get("https://api.navasan.tech/latest/?api_key=free")  # Replace if using paid API
        data = response.json()
        gold = data.get("geram18", {}).get("value", "نامشخص")
        dollar = data.get("usd", {}).get("value", "نامشخص")
        btc = data.get("btc", {}).get("value", "نامشخص")
        return f"\n💰 قیمت روز:\nدلار: {dollar}\nطلای ۱۸ عیار: {gold}\nبیت‌کوین: {btc} تومان"
    except:
        return "❗ دریافت نرخ روز ممکن نشد."

# === Main Menu ===
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📡 تحلیل اخبار جهانی", callback_data="global_news")],
        [InlineKeyboardButton("🗞 تحلیل اخبار ایران", callback_data="iran_news")],
        [InlineKeyboardButton("🌐 تحلیل ترکیبی (جهانی + ایران)", callback_data="mixed_news")],
        [InlineKeyboardButton("💰 نرخ روز طلا، دلار و رمزارز", callback_data="daily_rate")],
        [InlineKeyboardButton("ℹ️ راهنما", callback_data="help")]
    ])

# === Command /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! به ربات تحلیل‌گر بازار خوش آمدید. یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=main_menu()
    )

# === Handle Callback Queries ===
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "global_news":
        articles = fetch_news_newsapi() + fetch_news_gnews() + fetch_news_mediastack()
        full_text = "\n".join([translate(a.get("title", "")) for a in articles])
        signal = analyze_news(full_text)
        await query.message.reply_text(f"🌐 تحلیل اخبار جهانی:\n{full_text}\n\n📊 نتیجه: {signal}")

    elif query.data == "iran_news":
        articles = fetch_news_newsdata()
        full_text = "\n".join([a.get("title", "") for a in articles])
        signal = analyze_news(full_text)
        await query.message.reply_text(f"🇮🇷 تحلیل اخبار داخلی:\n{full_text}\n\n📊 نتیجه: {signal}")

    elif query.data == "mixed_news":
        articles = fetch_news_newsapi() + fetch_news_newsdata()
        full_text = "\n".join([translate(a.get("title", "")) for a in articles])
        signal = analyze_news(full_text)
        await query.message.reply_text(f"📊 تحلیل ترکیبی:\n{full_text}\n\n📈 نتیجه: {signal}")

    elif query.data == "daily_rate":
        rates = fetch_daily_rates()
        await query.message.reply_text(rates)

    elif query.data == "help":
        await query.message.reply_text("برای دریافت تحلیل و نرخ‌ها، فقط دکمه‌های منو را فشار دهید. هر بار تحلیل جدیدی برایتان ارسال می‌شود.")

# === Bot Initialization ===
app = ApplicationBuilder().token("توکن ربات شما را اینجا بگذارید").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.run_polling()
