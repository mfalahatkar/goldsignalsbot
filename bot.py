# telegram_news_bot.py
import requests
from bs4 import BeautifulSoup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext, CallbackQueryHandler
from deep_translator import GoogleTranslator

# توکن ربات تلگرام
BOT_TOKEN = "7721073253:AAGq1z2wcdI68SdW06a3xo88dMOGycmcJoY"

# توکن‌های منابع خبری
NEWSAPI_TOKEN = "27284966a77a4619a5c89846514cb284"
GNEWS_TOKEN = "cc588426fdda5e76dd8e4f8f7706616e"
MEDIASTACK_TOKEN = "c50464aae1764f79a272dfaa41cf478f"
NEWSDATA_TOKEN = "api_live_OQyfGEsKxBWbMbIv2g5VBZXIxlKcQTMiI5Va5tccJ2"

# تابع دریافت نرخ ارز و طلا از tgju.org
def get_tgju_rates():
    try:
        response = requests.get("https://www.tgju.org")
        soup = BeautifulSoup(response.text, "html.parser")

        def extract_price(code):
            el = soup.find("td", {"data-market-row": code})
            return el.find("span", class_="info-price") if el else None

        rates = {
            "دلار": extract_price("usd") or "نامشخص",
            "یورو": extract_price("eur") or "نامشخص",
            "سکه": extract_price("sekebahar") or "نامشخص",
            "طلا": extract_price("geram18") or "نامشخص",
            "بیت کوین": extract_price("btc") or "نامشخص",
        }

        return {k: v.get_text(strip=True) if v else "نامشخص" for k, v in rates.items()}
    except Exception as e:
        return {"خطا": str(e)}

# تابع دریافت اخبار از NewsAPI
def get_newsapi_news():
    url = f"https://newsapi.org/v2/top-headlines?q=gold+OR+dollar+OR+crypto+OR+oil+OR+war&language=en&apiKey={NEWSAPI_TOKEN}"
    try:
        r = requests.get(url)
        data = r.json()
        articles = data.get("articles", [])[:5]
        translated_news = []
        for article in articles:
            title = article.get("title", "")
            desc = article.get("description", "")
            translated = GoogleTranslator(source='auto', target='fa').translate(f"{title}\n{desc}")
            translated_news.append(translated)
        return translated_news
    except Exception as e:
        return [f"خطا در دریافت اخبار: {e}"]

# دکمه‌های منو
keyboard = [
    [InlineKeyboardButton("📊 نرخ روز", callback_data='rates')],
    [InlineKeyboardButton("🌍 اخبار جهانی", callback_data='global_news')],
    [InlineKeyboardButton("🇮🇷 اخبار ایران", callback_data='iran_news')],
    [InlineKeyboardButton("📡 تحلیل ترکیبی", callback_data='combined_analysis')],
]

markup = InlineKeyboardMarkup(keyboard)

# دستور start
def start(update: Update, context: CallbackContext):
    update.message.reply_text("به ربات تحلیل اقتصادی خوش آمدید 👋", reply_markup=markup)

# مدیریت دکمه‌ها
def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == "rates":
        rates = get_tgju_rates()
        msg = "\n".join([f"{k}: {v}" for k, v in rates.items()])
        query.edit_message_text(text=f"نرخ‌های روز:\n{msg}", reply_markup=markup)

    elif query.data == "global_news":
        news = get_newsapi_news()
        query.edit_message_text(text="\n\n".join(news), reply_markup=markup)

    elif query.data == "iran_news":
        query.edit_message_text(text="درحال توسعه اخبار فارسی از منابع داخلی مثل Mehrnews و Farsnews...", reply_markup=markup)

    elif query.data == "combined_analysis":
        rates = get_tgju_rates()
        news = get_newsapi_news()
        msg = "📊 نرخ‌ها:\n" + "\n".join([f"{k}: {v}" for k, v in rates.items()])
        msg += "\n\n📰 اخبار:\n" + "\n\n".join(news)
        query.edit_message_text(text=msg, reply_markup=markup)

# راه‌اندازی ربات
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
