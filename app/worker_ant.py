import os
import json
from app.pipeline import process_init, proccess_audio
import multiprocessing as mp


def worker_ant(queue: mp.Queue, err_queue: mp.Queue):
    models = process_init()

    err_queue.put(True)  # сообщаем главному потоку, что проинициализировались

    while True:
        audiofile_path = queue.get()
        try:  # try...except чтобы сервер не падал из-за ошибок

            open(audiofile_path+'.blocked', 'wb')  # aka mutex
            enhanced_audio_path, text, words = proccess_audio(*models)

            response_json = {
                "text": text,
                "words": words
            }

            with open(audiofile_path+'.json', 'w', encoding='utf8') as outfile:
                json.dump(response_json, outfile, ensure_ascii=False)
            os.remove(audiofile_path+'.blocked')

        except BaseException as err:
            print(err)
            err_queue.put(audiofile_path, 0)

            with open(audiofile_path+'.error', 'w', encoding='utf-8') as error_logger:
                error_logger.write(repr(err))
            os.remove(audiofile_path+'.blocked')
