#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple Bot to calculate BMI-index through Telegram messenger.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Replace your token.
Install required libraries.
Run python bot.py
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""



import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)
import enum
import settings

BOT_COMMANDS = ['start', 'help', 'calc']
TOKEN = settings.TOKEN
GENDER, WEIGHT, HEIGHT = range(3)
WELCOME_MESSAGE = "Hello. Welocme to the BMI-Index calculator Bot!\n"
INSTRUCTION_MESSAGE = "Please enter your gender, then your weight and then your height in kilograms and centimeters respectively:\n"
CANCEL_INSTRUCTION_MESSAGE = "(You can cancel the calculation by entering /cancel command)\n"
NEW_CALC_INSTRUCTION_MESSAGE = "You can have a new calculation anytime. Just enter the '/calc' command.\n"

data = {'weight': "", 'height': "", 'gender': ""}

class Gender(enum.Enum):
    Man = "Man"
    Woman = "Woman"


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def get_bmi(weight, height)->float:
    height_m = int(height)/100
    bmi = float(weight)/(height_m*height_m)
    return bmi


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, context: CallbackContext) -> int:
    """Send a message when the command /start is issued."""
    global data
    data = {'weight': "", 'height': "", 'gender': ""}
    reply_keyboard = [["Man", "Woman"]]
    update.message.reply_text(
        WELCOME_MESSAGE + INSTRUCTION_MESSAGE + CANCEL_INSTRUCTION_MESSAGE,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Are you a Man or a Woman?'
        ),
    )
    return GENDER


def get_gender(update: Update, context: CallbackContext) -> int:
    """Stores the selected gender and asks for a weight afterwards."""
    user = update.message.from_user
    data['gender'] = update.message.text
    logger.info("Gender of %s: %s", user.first_name, update.message.text)
    update.message.reply_text(
        'Great! Now please enter your WEIGHT in kilograms: '
            + CANCEL_INSTRUCTION_MESSAGE,
        reply_markup=ReplyKeyboardRemove(),
    )
    return WEIGHT


def get_weight(update: Update, context: CallbackContext) -> int:
    """Stores the user's weight and ends the conversation."""
    user = update.message.from_user
    data['weight'] = update.message.text
    weight = update.message.text
    logger.info("Weight of %s: %s", user.first_name, weight)
    update.message.reply_text('Great! Now please enter your HEIGHT in centimeters: '
            + CANCEL_INSTRUCTION_MESSAGE)
    return HEIGHT


def get_height(update: Update, context: CallbackContext) -> int:
    """Stores the user's height and ends the conversation."""
    user = update.message.from_user
    data['height'] = update.message.text
    bmi = get_bmi(data['weight'], data['height'])
    logger.info("Height of %s: %s", user.first_name, update.message.text)
    update.message.reply_text('Thank you!\nyour BMI is: '+  str(bmi)
            + NEW_CALC_INSTRUCTION_MESSAGE,
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def normalCancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Bye! I hope I can help you again with a new calculation some day.\n'
            +NEW_CALC_INSTRUCTION_MESSAGE,
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def new_calc(update: Update, context: CallbackContext)-> int:
    """Send a message when the command /calc is issued."""
    reply_keyboard = [["Man", "Woman"]]
    update.message.reply_text(
        INSTRUCTION_MESSAGE + CANCEL_INSTRUCTION_MESSAGE,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Are you a Man or a Woman?'
        ),
    )
    return GENDER


def help(update: Update, context: CallbackContext):
    """Send a message when the command /help is issued."""
    update.message.reply_text('HELP!')
    context.bot.send_message(chat_id = update.effective_chat.id, text="HELP!")


def echo(update: Update, context: CallbackContext):
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def unknown(update: Update, context: CallbackContext):
    """"Tell them the command format is not correct. """
    update.message.reply_text("Sorry, Such command does not exist. Please Try again.")


def error(update: Update, context: CallbackContext):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on start commands - have a small conversation
    start_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            GENDER: [MessageHandler(Filters.regex('^(Man|Woman)$'), get_gender)],
            WEIGHT: [MessageHandler(Filters.text & ~Filters.command, get_weight)],
            HEIGHT: [MessageHandler(Filters.text & ~Filters.command, get_height)],
        },
        fallbacks=[ CommandHandler('cancel', normalCancel),
                    MessageHandler(Filters.regex('/calc'), new_calc),
                    MessageHandler(Filters.regex('/start'), start)],
    )
    dp.add_handler(start_conv_handler)

    #on help command, show user some instructions.
    dp.add_handler(CommandHandler("help", help))

    #on calc command, help user have a new calculation.
    new_clc_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('calc', new_calc)],
        states={
            GENDER: [MessageHandler(Filters.regex('^(Man|Woman)$'), get_gender)],
            WEIGHT: [MessageHandler(Filters.text & ~Filters.command, get_weight)],
            HEIGHT: [MessageHandler(Filters.text & ~Filters.command, get_height)],
        },
        fallbacks=[ CommandHandler('cancel', normalCancel),
                    MessageHandler(Filters.regex('/calc'), new_calc),
                    MessageHandler(Filters.regex('/start'), start)],
    )
    dp.add_handler(new_clc_conv_handler)

    # on non-command message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text & (~Filters.command), echo))

    # on commands which are not defined
    dp.add_handler(MessageHandler(Filters.command, unknown))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()