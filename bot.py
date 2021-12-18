from config import TELEGRAM_TOKEN
import defi
import logging, datetime, pytz
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import (
    Updater,
    CallbackContext,
    CommandHandler,
    InlineQueryHandler,
    MessageHandler,
    Filters,
    JobQueue,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
dispatcher = updater.dispatcher


def monitor_portfolio_start(update: Update, context: CallbackContext):
    context.job_queue.start()
    context.job_queue.run_repeating(summary, 3600, context=update.message.chat_id)
    context.job_queue.run_repeating(alert_actions, 600, context=update.message.chat_id)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Monitoring...")


def monitor_portfolio_stop(update: Update, context: CallbackContext):
    context.job_queue.stop()
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="Monitoring Stopped..."
    )


def summary(context):
    coin_data = defi.get_coin_data()
    summary = defi.rtn_summary(coin_data)
    context.bot.send_message(context.job.context, text=summary, parse_mode="HTML")


def alert_actions(context):
    coin_data = defi.get_coin_data()
    chat_text = defi.recommendations(coin_data)
    if len(chat_text) > 0:
        context.bot.send_message(context.job.context, text=chat_text, parse_mode="HTML")


dispatcher.add_handler(
    CommandHandler("monitor_portfolio", monitor_portfolio_start, pass_job_queue=True)
)
dispatcher.add_handler(
    CommandHandler("stop", monitor_portfolio_stop, pass_job_queue=True)
)

updater.start_polling()
updater.idle()
