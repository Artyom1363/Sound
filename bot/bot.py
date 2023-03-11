import os

import telebot


def bot_init():
    # создаем объект бота
    bot = telebot.TeleBot(os.environ.get("TG_BOT_TOKEN"))
    # обработчик любых сообщений
    @bot.message_handler(func=lambda message: True)
    def echo_all(message):
        bot.reply_to(message, message.text)
        print("New message!")

    # запускаем бота
    bot.polling()
