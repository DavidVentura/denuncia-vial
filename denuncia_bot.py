#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from enum import Enum
from functools import wraps
from random import getrandbits
from telegram.ext.dispatcher import run_async
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

from lib.denunciar import complaint

import json
import os

CONFIG = json.loads(open('telegram.json').read())
AUTHORIZED_USERS = CONFIG['ids']
user_state = {}


class states(Enum):
    WAITING_FIRST_IMAGE = 1
    WAITING_SECOND_IMAGE = 2
    WAITING_PLATE = 3
    WAITING_CONFIRMATION_PLATE = 4
    WAITING_OBS = 5
    WAITING_CONFIRMATION_OBS = 6
    FINISHED = 7


def error_callback(bot, update, error):
    print(error)


def restricted(func):
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        user_id = update.message.from_user.id
        if user_id not in AUTHORIZED_USERS:
            error_msg = "Unauthorized access denied for {}.".format(user_id)
            bot.sendMessage(chat_id=update.message.chat.id, text=error_msg)
            return
        return func(bot, update, *args, **kwargs)
    return wrapped


@restricted
def start(bot, update):
    user_id = update.message.from_user.id
    user_state[user_id] = {'state': states.WAITING_FIRST_IMAGE}
    update.message.reply_text('Send me the first image')


# @run_async
@restricted
def confirm(bot, update):
    user_id = update.message.from_user.id
    if (user_id not in user_state or user_state[user_id]['state'] !=
       states.WAITING_CONFIRMATION_PLATE):
        update.message.reply_text("You can't confirm right now!")
        return
    state = user_state[user_id]
    update.message.reply_text('Complaining...')
    response = complaint('obs', state['plate'], state['file1'], state['file2'])
    update.message.reply_text('Confirmed (%s)' % response)


@run_async
def image(bot, update):
    user_id = update.message.from_user.id
    if (user_id not in user_state or user_state[user_id]['state'] not in
            [states.WAITING_FIRST_IMAGE, states.WAITING_SECOND_IMAGE]):
        update.message.reply_text("You can't send images yet!")
        return
    photos = update.message.photo
    photo = photos[-1]  # best quality

    file_id = photo.file_id
    f = bot.get_file(file_id)

    fname = "%s-%x.jpg" % (user_id, getrandbits(64))
    fname = os.path.join("/tmp/", fname)
    f.download(fname)
    state = user_state[user_id]
    if state['state'] == states.WAITING_FIRST_IMAGE:
        state['file1'] = fname
        state['state'] = states.WAITING_SECOND_IMAGE
        update.message.reply_text("Ok, send me the next image")
    elif state['state'] == states.WAITING_SECOND_IMAGE:
        state['file2'] = fname
        state['state'] = states.WAITING_PLATE
        update.message.reply_text("Ok, send me the plate")


def text(bot, update):
    user_id = update.message.from_user.id
    if (user_id not in user_state or user_state[user_id]['state'] not in
       [states.WAITING_PLATE, states.WAITING_CONFIRMATION_PLATE,
       states.WAITING_OBS, states.WAITING_CONFIRMATION_OBS]):
        update.message.reply_text("You can't send text right now!")
        return

    if (user_state[user_id]['state'] in
       [states.WAITING_PLATE, states.WAITING_CONFIRMATION_PLATE]):
        plate = update.message.text.strip().replace(' ', '')
        user_state[user_id]['plate'] = plate
        user_state[user_id]['state'] = states.WAITING_CONFIRMATION_PLATE
        print("WAITING_CONFIRMATION_PLATE")
    else:
        user_state[user_id]['obs'] = update.message.text.strip()
        user_state[user_id]['state'] = states.WAITING_CONFIRMATION_OBS
        print("WAITING_CONFIRMATION_OBS")

    s_confirm = "If you want to confirm, send /confirm\n"
    s_confirm += "if you want to change the plate/obs, just send it again"
    bot.sendMessage(chat_id=update.message.chat.id, text=s_confirm)


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(CONFIG['token'])

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("confirm", confirm))
    # updater.dispatcher.add_handler(CallbackQueryHandler(button))
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, text))
    dp.add_handler(MessageHandler(Filters.photo, image))

    dp.add_error_handler(error_callback)

    # log all errors
    # dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling(clean=True)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    print("Ready.")
    updater.idle()


if __name__ == '__main__':
    main()
