import os

import telebot


def bot_init():
    # создаем объект бота
    bot = telebot.TeleBot(os.environ.get("TG_BOT_TOKEN"))

    # обработчик любых сообщений

    @bot.message_handler(content_types=['text'])
    def chat(message):
        if message.text == 'Привет':
            bot.send_message(message.from_user.id,
                             'Отправь аудио или голосовуху боту. Он почистит твой голос от мата и паразитных слов.')

    @bot.message_handler(content_types=['audio', 'voice'])
    def file_process(message):
        bot.send_message(message.from_user.id, 'Аудио получено. Подожди немного...')
        if message.content_type == 'audio':
            file_info = bot.get_file(message.audio.file_id)
        if message.content_type == 'voice':
            file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open('storage/' + file_info.file_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        print('Download completed')

        with open('storage/' + file_info.file_path, 'rb') as file:
            if message.content_type == 'audio':
                bot.send_audio(message.from_user.id, audio=file)
            if message.content_type == 'voice':
                bot.send_voice(message.from_user.id, voice=file)

        print('Send completed')

    # запускаем бота
    bot.polling()
