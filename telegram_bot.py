from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def start(update, context):
  update.message.reply_text('輸入月份:',
    reply_markup = InlineKeyboardMarkup(
      [
        [InlineKeyboardButton(str(m), callback_data = '{}'.format(m)) for m in range(1, 7)],
        [InlineKeyboardButton(str(m), callback_data = '{}'.format(m)) for m in range(7, 13)]
      ]
      ))

def answer(update, context):
    bm = update.callback_query.data

def main():
  updater = Updater(token='1893410568:AAHjzrw8EfE3cAv1tjWZ2okgLvmLals3gN8', request_kwargs={'proxy_url': 'http://192.168.61.211:80'})
  updater.dispatcher.add_handler(CommandHandler('start', start))
  updater.dispatcher.add_handler(CallbackQueryHandler(answer))
  updater.start_polling()
  updater.idle()

if __name__ == "__main__":
    main()