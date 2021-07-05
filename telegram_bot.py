from telegram.ext import Updater, CommandHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def start(bot, update):
  bot.message.reply_text('hello, {}'.format(bot.message.from_user.first_name),
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(str(s), callback_data = '{}'.format(s)) for s in range(1, 12)]]))

updater = Updater(token='1893410568:AAHjzrw8EfE3cAv1tjWZ2okgLvmLals3gN8', request_kwargs={'proxy_url': 'http://192.168.61.211:80'})

updater.dispatcher.add_handler(CommandHandler('start', start))

updater.start_polling()
updater.idle()