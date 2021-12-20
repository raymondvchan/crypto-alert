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


def remove_job_if_exists(name: str, context: CallbackContext) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


def monitor_portfolio_start(update: Update, context: CallbackContext):
    # context.job_queue.start()
    chat_id = update.message.chat_id
    try:
        job_removed = remove_job_if_exists(str(chat_id), context)

        context.job_queue.run_repeating(
            summary, 3600, context=chat_id, name=str(chat_id) + "summary"
        )
        context.job_queue.run_repeating(
            alert_actions, 3600, context=chat_id, name=str(chat_id) + "alert"
        )
        text = "Monitoring..."
        if job_removed:
            text += " Old job removed"
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    except Exception as e:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error: {e}")


def monitor_portfolio_stop(update: Update, context: CallbackContext):
    # context.job_queue.stop()
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id) + "summary", context)
    job_removed = remove_job_if_exists(str(chat_id) + "alert", context)
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
