import html
import random
import vexana.modules.truth_and_dare_string as truth_and_dare_string
from telegram import ParseMode, Update, Bot
from telegram.ext import CallbackContext, run_async
from vexana import dispatcher
from vexana.modules.disable import DisableAbleCommandHandler


def truth(update: Update, context: CallbackContext):
    args = context.args
    update.effective_message.reply_text(random.choice(truth_and_dare_string.TRUTH))


def dare(update: Update, context: CallbackContext):
    args = context.args
    update.effective_message.reply_text(random.choice(truth_and_dare_string.DARE))


TRUTH_HANDLER = DisableAbleCommandHandler("truth", truth, run_async=True)
DARE_HANDLER = DisableAbleCommandHandler("dare", dare, run_async=True)

dispatcher.add_handler(TRUTH_HANDLER)
dispatcher.add_handler(DARE_HANDLER)
