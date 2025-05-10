import os
import requests
from bs4 import BeautifulSoup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from deep_translator import GoogleTranslator

# توکن ربات تلگرام
TELEGRAM_BOT_TOKEN = "7721073253:AAGq1z2wcdI68SdW06a3xo88dMOGycmcJoY"

# توکن‌های API
NEWSAPI_TOKEN = "توکن NewsAPI شما"
GNEWS_TOKEN = "cc588426fdda5e76dd8e4f8f7706616e"
MEDIASTACK_TOKEN = "c50464aae1764f79a272dfaa41cf478f"
NEWSDATA_TOKEN = "api_live_OQyfGEsKxBWbMbIv2g5VBZXIxlKcQTMiI5Va5tccJ2"

# تابع برای ترجمه متن به فارسی
def translate_to_farsi(text):
    try:
        return GoogleTranslator(source='auto', target='fa').translate(text)
    except Exception as e:
        return f"خطا در ترجمه: {e}"

# تابع برای دریافت نرخ‌های روز از tgju.org
def get_live_rates():
    try:
        url = "https://www.tgju.org/"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # استخراج نرخ‌ها
        rates = {}
        items = soup.find_all('tr', class_='pointer')
        for item in items:
            name = item.find('td', class_='first').get_text(strip=True)
            price = item.find('td', class_='nf').get_text(strip=True)
            rates[name] = price

        message = "📊 نرخ‌های روز:\n"
        for key, value in rates.items():
            message += f"{key}: {value}\n"

        return message
    except Exception as e:
        return f"خطا در دریافت نرخ‌ها: {e}"

# تابع برای دریافت اخبار از NewsAPI
def get_newsapi_news():
    try:
        url = f"https://newsapi.org/v2/top-headlines?language=en&apiKey={NEWSAPI_TOKEN}"
        response = requests.get(url)
        data = response.json()
        articles = data.get('articles', [])[:5]

        message = "📰 اخبار از NewsAPI:\n"
        for article in articles:
            title = translate_to_farsi(article.get('title', ''))
            url = article.get('url', '')
            message += f"- {title}\n{url}\n"

        return message
    except Exception as e:
        return f"خطا در دریافت اخبار: {e}"

# تابع برای دریافت اخبار از GNews
def get_gnews_news():
    try:
        url = f"https://gnews.io/api/v4/top-headlines?lang=en&token={GNEWS_TOKEN}"
        response = requests.get(url)
        data = response.json()
        articles = data.get('articles', [])[:5]

        message = "📰 اخبار از GNews:\n"
        for article in articles:
            title = translate_to_farsi(article.get('title', ''))
            url = article.get('url', '')
            message += f"- {title}\n{url}\n"

        return message
    except Exception as e:
        return f"خطا در دریافت اخبار: {e}"

# تابع برای دریافت اخبار از Mediastack
def get_mediastack_news():
    try:
        url = f"http://api.mediastack.com/v1/news?access_key={MEDIASTACK_TOKEN}&languages=en"
        response = requests.get(url)
        data = response.json()
        articles = data.get('data', [])[:5]

        message = "📰 اخبار از Mediastack:\n"
        for article in articles:
            title = translate_to_farsi(article.get('title', ''))
            url = article.get('url', '')
            message += f"- {title}\n{url}\n"

        return message
    except Exception as e:
        return f"خطا در دریافت اخبار: {e}"

# تابع برای دریافت اخبار از NewsData.io
def get_newsdata_news():
    try:
        url = f"https://newsdata.io/api/1/news?apikey={NEWSDATA_TOKEN}&language=en"
        response = requests.get(url)
        data = response.json()
        articles = data.get('results', [])[:5]

        message = "📰 اخبار از NewsData.io:\n"
        for article in articles:
            title = translate_to_farsi(article.get('title', ''))
            url = article.get('link', '')
            message += f"- {title}\n{url}\n"

        return message
    except Exception as e:
        return f"خطا در دریافت اخبار: {e}"

# هندلر برای شروع
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("اخبار ایران", callback_data='iran_news')],
        [InlineKeyboardButton("اخبار جهان", callback_data='world_news')],
        [InlineKeyboardButton("تحلیل ترکیبی", callback_data='combined_analysis')],
        [InlineKeyboardButton("نرخ‌های روز", callback_data='live_rates')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('لطفاً یک گزینه را انتخاب کنید:', reply_markup=reply_markup)

# هندلر برای دکمه‌ها
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'iran_news':
        news = get_newsdata_news()
        await query.edit_message_text(text=news)
    elif query.data == 'world_news':
        news = get_newsapi_news()
        await query.edit_message_text(text=news)
    elif query.data == 'combined_analysis':
        news1 = get_newsapi_news()
        news2 = get_gnews_news()
        news3 = get_mediastack_news()
        news4 = get_newsdata_news()
        combined_news = f"{news1}\n{news2}\n{news3}\n{news4}"
        await query.edit_message_text(text=combined_news)
    elif query.data == 'live_rates':
        rates = get_live_rates()
        await query.edit_message_text(text=rates)

# اجرای ربات
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.run_polling()

if __name__ == '__main__':
    main()
