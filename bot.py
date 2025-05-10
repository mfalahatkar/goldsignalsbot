import logging
import requests
from bs4 import BeautifulSoup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from deep_translator import GoogleTranslator

# ---------------------- CONFIG ----------------------
TELEGRAM_TOKEN = "7721073253:AAGq1z2wcdI68SdW06a3xo88dMOGycmcJoY"
NEWSAPI_TOKEN = "27284966a77a4619a5c89846514cb284"
GNEWS_TOKEN = "cc588426fdda5e76dd8e4f8f7706616e"
MEDIASTACK_TOKEN = "c50464aae1764f79a272dfaa41cf478f"
NEWSDATA_TOKEN = "api_live_OQyfGEsKxBWbMbIv2g5VBZXIxlKcQTMiI5Va5tccJ2"

# ---------------------- LOGGER ----------------------
logging.basicConfig(level=logging.INFO)

# ---------------------- HANDLERS ----------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🌍 اخبار جهانی", callback_data="global")],
        [InlineKeyboardButton("🇮🇷 اخبار ایران", callback_data="iran")],
        [InlineKeyboardButton("📡 تحلیل ترکیبی", callback_data="combined")],
        [InlineKeyboardButton("📊 نرخ روز", callback_data="rates")]
    ]
    await update.message.reply_text("یکی از گزینه‌های زیر را انتخاب کنید:",
                                    reply_markup=InlineKeyboardMarkup(keyboard))

# ---------------------- TRANSLATOR ----------------------
def translate(text):
    try:
        return GoogleTranslator(source='auto', target='fa').translate(text)
    except:
        return text

# ---------------------- GLOBAL NEWS ----------------------
def fetch_global_news():
    try:
        url = f"https://newsapi.org/v2/top-headlines?category=business&language=en&apiKey={NEWSAPI_TOKEN}"
        res = requests.get(url).json()
        return [article["title"] for article in res.get("articles", [])[:5]]
    except:
        return []

# ---------------------- IRAN NEWS ----------------------
def fetch_iran_news():
    try:
        url = f"https://newsdata.io/api/1/news?apikey={NEWSDATA_TOKEN}&country=ir&language=fa"
        res = requests.get(url).json()
        return [article["title"] for article in res.get("results", [])[:5]]
    except:
        return []

# ---------------------- EXCHANGE RATES ----------------------
def fetch_rates():
    try:
        response = requests.get("https://www.tgju.org/")
        soup = BeautifulSoup(response.text, "lxml")

        dollar = soup.find("td", class_="nf" , text="دلار آزاد").find_next_sibling("td").text.strip()
        gold = soup.find("td", class_="nf", text="طلای 18 عیار").find_next_sibling("td").text.strip()
        coin = soup.find("td", class_="nf", text="سکه امامی").find_next_sibling("td").text.strip()

        btc = requests.get("https://api.coindesk.com/v1/bpi/currentprice/BTC.json").json()
        bitcoin = btc["bpi"]["USD"]["rate"]

        return f"💵 دلار: {dollar}\n🪙 سکه: {coin}\n📈 طلا: {gold}\n₿ بیت‌کوین: {bitcoin} دلار"
    except Exception as e:
        return f"❌ خطا در دریافت نرخ‌ها"

# ---------------------- CALLBACKS ----------------------
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "global":
        news = fetch_global_news()
        translated = [translate(n) for n in news]
        await query.edit_message_text("\n".join(translated) or "❌ خبری یافت نشد.")

    elif data == "iran":
        news = fetch_iran_news()
        await query.edit_message_text("\n".join(news) or "❌ خبری یافت نشد.")

    elif data == "rates":
        rates = fetch_rates()
        await query.edit_message_text(rates)

    elif data == "combined":
        ir_news = fetch_iran_news()
        gl_news = fetch_global_news()
        translated = [translate(n) for n in gl_news]
        rates = fetch_rates()

        message = f"📰 تحلیل ترکیبی:\n\n🇮🇷 مهم‌ترین اخبار ایران:\n{chr(10).join(ir_news)}\n\n🌍 اخبار جهانی مهم:\n{chr(10).join(translated)}\n\n📊 نرخ‌ها:\n{rates}"
        await query.edit_message_text(message)

# ---------------------- MAIN ----------------------
if __name__ == '__main__':
    app = Application.builder().token("7721073253:AAGq1z2wcdI68SdW06a3xo88dMOGycmcJoY").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.run_polling()
