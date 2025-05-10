# bot.py

import logging
import requests
from bs4 import BeautifulSoup
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# تنظیم توکن ربات
TELEGRAM_BOT_TOKEN = "7721073253:AAGq1z2wcdI68SdW06a3xo88dMOGycmcJoY"

# پیکربندی لاگ‌ها
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# منابع خبری
NEWSAPI_TOKEN = "27284966a77a4619a5c89846514cb284"
GNEWS_TOKEN = "cc588426fdda5e76dd8e4f8f7706616e"
MEDIASTACK_TOKEN = "c50464aae1764f79a272dfaa41cf478f"
NEWSDATA_IO_IRAN = "api_live_OQyfGEsKxBWbMbIv2g5VBZXIxlKcQTMiI5Va5tccJ2"

# توابع دریافت اخبار

def get_iran_news():
    try:
        response = requests.get("https://www.mehrnews.com/service/Economy")
        soup = BeautifulSoup(response.text, "html.parser")
        titles = soup.select(".news a.title")
        news = [title.get_text(strip=True) for title in titles[:5]]
        return news
    except Exception as e:
        logger.error("خطا در دریافت اخبار ایران: %s", e)
        return ["❌ خطا در دریافت اخبار ایران"]

def get_global_news():
    try:
        url = f"https://newsapi.org/v2/top-headlines?category=business&language=en&apiKey={NEWSAPI_TOKEN}"
        res = requests.get(url).json()
        return [article['title'] for article in res.get("articles", [])[:5]]
    except Exception as e:
        logger.error("خطا در دریافت اخبار جهانی: %s", e)
        return ["❌ خطا در دریافت اخبار جهانی"]

def get_rates():
    try:
        response = requests.get("https://www.tgju.org/")
        soup = BeautifulSoup(response.text, "html.parser")
        data = {}
        for key in ["price_dollar_rl", "price_sekee", "price_old_gold", "crypto-bitcoin"]:
            tag = soup.find("td", id=key)
            if tag:
                data[key] = tag.text.strip()
        return data
    except Exception as e:
        logger.error("خطا در دریافت نرخ‌ها: %s", e)
        return {}

# فرمان شروع
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("🇮🇷 اخبار ایران"), KeyboardButton("🌍 اخبار جهانی")],
        [KeyboardButton("📡 تحلیل ترکیبی"), KeyboardButton("📊 نرخ روز")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("سلام! یکی از گزینه‌ها را انتخاب کنید:", reply_markup=reply_markup)

# پردازش پیام‌ها
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🇮🇷 اخبار ایران":
        news = get_iran_news()
        await update.message.reply_text("\n\n".join(news))

    elif text == "🌍 اخبار جهانی":
        news = get_global_news()
        await update.message.reply_text("\n\n".join(news))

    elif text == "📊 نرخ روز":
        rates = get_rates()
        if rates:
            message = f"💵 دلار: {rates.get('price_dollar_rl', '---')}\n"
            message += f"🪙 سکه: {rates.get('price_sekee', '---')}\n"
            message += f"📈 طلای ۱۸ عیار: {rates.get('price_old_gold', '---')}\n"
            message += f"₿ بیت‌کوین: {rates.get('crypto-bitcoin', '---')}"
            await update.message.reply_text(message)
        else:
            await update.message.reply_text("❌ خطا در دریافت نرخ‌ها")

    elif text == "📡 تحلیل ترکیبی":
        iran_news = get_iran_news()
        global_news = get_global_news()
        rates = get_rates()
        message = "📰 تحلیل ترکیبی:\n"
        message += "\n🇮🇷 مهم‌ترین اخبار ایران:\n" + "\n".join(iran_news[:3])
        message += "\n\n🌍 اخبار جهانی مهم:\n" + "\n".join(global_news[:3])
        message += "\n\n📊 نرخ‌ها:\n"
        message += f"💵 دلار: {rates.get('price_dollar_rl', '---')}\n"
        message += f"🪙 سکه: {rates.get('price_sekee', '---')}\n"
        message += f"📈 طلا: {rates.get('price_old_gold', '---')}\n"
        message += f"₿ بیت‌کوین: {rates.get('crypto-bitcoin', '---')}"
        await update.message.reply_text(message)

    else:
        await update.message.reply_text("دستور نامعتبر است. لطفاً یکی از گزینه‌های منو را انتخاب کنید.")

# راه‌اندازی ربات
if __name__ == '__main__':
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
