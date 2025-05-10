from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
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
            return "احتمال افزایش قیمت طلا و دلار وجود دارد. سیگنال خرید."

    for word in keywords_sell:
        if word in news_text:
            return "احتمال کاهش قیمت طلا و دلار وجود دارد. سیگنال فروش."

    return "خبر خاصی مشاهده نشد. سیگنالی صادر نمی‌شود."


# فرمان /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! من ربات تحلیلگر بازار طلا و دلار هستم.")

# فرمان /analyze
async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    news = get_news()
    signal = analyze_news(news.lower())
    await update.message.reply_text(f"اخبار منتخب:\n{news}\n\nتحلیل:\n{signal}")

# راه‌اندازی ربات
app = ApplicationBuilder().token("7721073253:AAGq1z2wcdI68SdW06a3xo88dMOGycmcJoY").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("analyze", analyze))
app.run_polling()
