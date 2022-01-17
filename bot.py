from distutils.cmd import Command
from config import TELEGRAM_TOKEN
import defi
from tarot import tarot_market
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


def monitor_tarot_start(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    try:
        job_removed = remove_job_if_exists(str(chat_id), context)

        context.job_queue.run_repeating(
            tarot_liquidation_check,
            600,
            context=chat_id,
            name=str(chat_id) + "tarot_liquidation_check",
        )
        text = "Monitoring..."
        if job_removed:
            text += " Old job removed"
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    except Exception as e:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error: {e}")


def tarot_liquidation_check(context):
    from tarot_config import markets

    for market in markets:
        cur_market = tarot_market(
            market["pairs"][0],
            market["pairs"][1],
            market["lower_bound"],
            market["upper_bound"],
        )
        is_safe_zone = cur_market.check_liquidation_bounds()
        if not is_safe_zone:
            text = f"""<b><u>!! LIQUIDATION WARNING !!</u></b>"""
            context.bot.send_message(context.job.context, text=text, parse_mode="HTML")
            text = f"""<b>Pool: {cur_market.asset_1} / {cur_market.asset_2}</b>
Warning Bounds: {cur_market.lower_bound_warning} - {cur_market.upper_bound_warning}
<b><u>Liquidation Bounds: {cur_market.lower_bound} - {cur_market.upper_bound}</u></b>
Current Price: <b>{cur_market.current_price}</b>"""
            context.bot.send_message(context.job.context, text=text, parse_mode="HTML")


def tarot_status(update: Update, context: CallbackContext):
    from tarot_config import markets

    chat_id = update.message.chat_id
    try:
        for market in markets:
            cur_market = tarot_market(
                market["pairs"][0],
                market["pairs"][1],
                market["lower_bound"],
                market["upper_bound"],
            )
            cur_market.check_liquidation_bounds()
            text = f"""<b>Pool: {cur_market.asset_1} / {cur_market.asset_2}</b>
Warning Bounds ({cur_market.warning_threshold * 100} %): {cur_market.lower_bound_warning} - {cur_market.upper_bound_warning}
<b><u>Liquidation Bounds: {cur_market.lower_bound} - {cur_market.upper_bound}</u></b>
Mid Bound: |------------------{round(((cur_market.upper_bound - cur_market.lower_bound) / 2), 2)}------------------|
Current Price: <b>{cur_market.current_price}</b>"""
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=text, parse_mode="HTML"
            )
    except Exception as e:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error: {e}")


def monitor_tarot_stop(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(
        str(chat_id) + "tarot_liquidation_check", context
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="Monitoring Stopped..."
    )


dispatcher.add_handler(
    CommandHandler("monitor_portfolio", monitor_portfolio_start, pass_job_queue=True)
)
dispatcher.add_handler(
    CommandHandler("stop", monitor_portfolio_stop, pass_job_queue=True)
)
dispatcher.add_handler(
    CommandHandler("tarotwatch", monitor_tarot_start, pass_job_queue=True)
)
dispatcher.add_handler(
    CommandHandler("tarotstop", monitor_tarot_stop, pass_job_queue=True)
)
dispatcher.add_handler(CommandHandler("tarot", tarot_status))


updater.start_polling()
updater.idle()
