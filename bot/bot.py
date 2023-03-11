import os

import telebot
from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.io.VideoFileClip import VideoFileClip

from convert import convert_video_to_audio_moviepy


# root_path = '/home/nikita/Sound/bot'

def prepare_storage_path(raw_path: str):
    path = raw_path[raw_path.find('/'):]
    print(path)
    return './storage' + path


def bot_init():
    # создаем объект бота
    bot = telebot.TeleBot(os.environ.get("TG_BOT_TOKEN"))
    os.makedirs(os.path.dirname('storage/'), exist_ok=True)

    @bot.message_handler(content_types=['text'])
    def chat(message):
        if message.text == 'Привет':
            bot.send_message(message.from_user.id,
                             'Отправь аудио, видео или голосовое боту. Он почистит твой голос от мата и паразитных слов.')

    @bot.message_handler(content_types=['audio', 'voice', 'video'])
    def file_process(message):
        # receive
        if message.content_type == 'audio':
            file_info = bot.get_file(message.audio.file_id)
        if message.content_type == 'voice':
            file_info = bot.get_file(message.voice.file_id)
        if message.content_type == 'video':
            file_info = bot.get_file(message.video.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        storage_file_path = prepare_storage_path(file_info.file_path)
        with open(storage_file_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        print('Download completed')
        bot.send_message(message.from_user.id, 'Аудио получено. Подожди немного...')

        if message.content_type == 'video':
            storage_video_file_path = storage_file_path
            storage_file_path = convert_video_to_audio_moviepy(storage_file_path)

        # -----------------
        # process code
        # -----------------


        picks = [3]
        # -----------------
        # pics audio
        # audio_clip = AudioFileClip(storage_file_path)
        # audio_beep = AudioFileClip("./media/beep.mp3").set_duration(1)
        # for pickTime in picks:
        #     audio_clip = CompositeAudioClip([audio_clip, audio_beep.set_start(pickTime)])
        # storage_file_path = prepare_storage_path("beep_" + storage_file_path[storage_file_path.find('/') + 1:])
        # audio_clip.write_audiofile(storage_file_path, fps=44100, codec="libmp3lame")
        # -----------------

        if message.content_type == 'video':
            video_clip = VideoFileClip(storage_video_file_path)
            audio_clip = AudioFileClip(storage_file_path)
            final_clip = video_clip.set_audio(audio_clip)
            storage_file_path = prepare_storage_path("final_" + storage_video_file_path[storage_video_file_path.find('/') + 1:])
            final_clip.write_videofile(storage_file_path)

        # send
        with open(storage_file_path, 'rb') as file:
            if message.content_type == 'audio':
                bot.send_audio(message.from_user.id, audio=file)
            if message.content_type == 'voice':
                bot.send_voice(message.from_user.id, voice=file)
            if message.content_type == 'video':
                bot.send_video(message.from_user.id, video=file)

        print('Send completed')

    bot.polling()
