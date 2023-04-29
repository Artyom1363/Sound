from df.enhance import enhance, init_df, load_audio, save_audio
import whisper
import whisperx
import os
from datetime import datetime
import multiprocessing as mp
import json
import random
import torchaudio
STORAGE = "./content"
DEVICE = 'cpu'


def add_timestamp(filename: str):
    """Добавляет время в название файла. Также добавляет рандомное число, чтобы файлы, присланные в одно время, не пересекались

    Args:
        filename (str): имя файла с расширением

    Returns:
        (str): имя файла с датой и временем и рандомным числом
    """
    return filename[:filename.rfind('.')] + '_'+datetime.now().strftime("%m-%d-%Y_%H.%M.%S")+str(random.random())+filename[filename.rfind('.'):]


def init_storage_path():
    """
    Инициализация папки с контентом, куда всё будет сохраняться
    """

    if not os.path.exists(STORAGE):
        os.mkdir(STORAGE)

    return STORAGE


def get_timestamps_and_profanity(result_dict, profanity_set):
    """Переформатирует вывод whisperX в ответ клиенту.
    P.S. поля tokens и probability имели смысл в stable-whisper. После 
    перехода на whisperX это просто заглушки(чтобы клиент не падал).
    Их всёравно не используют

    Args:
        result_dict (_type_): вывод whisperX
        profanity_set (_type_): frozenset матерных слов 

    Returns:
        List[Dict]: список словарей по каждому слову
    """

    words = []

    for word in result_dict:
        is_profanity = word['text'].lower() in profanity_set
        temp_word = {
            'word': word['text'],
            'start': word['start'],
            'end': word['end'],
            'is_profanity': is_profanity,
            'tokens': [1],
            'probability': 1.0
        }
        words.append(temp_word)

    return words


def get_profanity_set(filename: str):
    """Генерирует frozenset из матерных слов из файла. В файле матерные слова должны быть по строчкам.

    Args:
        filename (str): Имя файла

    Returns:
        frozenset: матерные слова
    """
    words = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            words.append(line[:-1].lower())
    return frozenset(words)


def process_init():
    """инициализация worker'а

    Returns:
        необходимые атрибуты
    """
    DFmodel, df_state, _ = init_df(
        post_filter=True, config_allow_defaults=True)
    whisper_model = whisper.load_model('small', device=DEVICE)
    profanity_set = get_profanity_set('profanity.txt')
    model_a, metadata = whisperx.load_align_model(
        language_code='ru', device=DEVICE)
    return whisper_model, DFmodel, df_state, profanity_set, model_a, metadata


def proccess_audio(audio_path, whisper_model, deepfilter_model, df_state, profanity_set, model_a, metadata):
    # возвращает audio, text и таймштампы с матами
    # df_state.sr() - частота дискретизации
    audio, sound_rate = torchaudio.load(audio_path)
    if DEVICE == "cuda":
        audio = audio.cuda()
    if sound_rate != df_state.sr():
        audio = torchaudio.functional.resample(
            audio, sound_rate, df_state.sr(), lowpass_filter_width=128)

    
    enhanced = enhance(deepfilter_model, df_state, audio)
    enhanced_audio_path = audio_path[:audio_path.rfind('.')]+"_enhanced.wav"
    save_audio(enhanced_audio_path, enhanced, df_state.sr())

    result = whisper_model.transcribe(enhanced_audio_path, language='ru')

    # align whisper output
    result_aligned = whisperx.align(
        result["segments"], model_a, metadata, enhanced_audio_path, DEVICE)

    # result_dict = result.to_dict()
    text = result["text"]
    words = get_timestamps_and_profanity(
        result_aligned['word_segments'], profanity_set)

    return enhanced_audio_path, text, words


def worker_ant(queue: mp.Queue, err_queue: mp.Queue):
    whisper_model, DFmodel, df_state, profanity_set, model_a, metadata = process_init()
    while True:
        audiofile_path = queue.get()
        # try:

        open(audiofile_path+'.blocked', 'wb')  # aka mutex
        enhanced_audio_path, text, words = proccess_audio(
            audiofile_path, whisper_model, DFmodel, df_state, profanity_set, model_a, metadata)
        response_json = {
            "text": text,
            "words": words
        }
        with open(audiofile_path+'.json', 'w', encoding='utf8') as outfile:
            json.dump(response_json, outfile, ensure_ascii=False)
        os.remove(audiofile_path+'.blocked')
        # except BaseException as e:
        #     print(e)
        #     err_queue.put(audiofile_path, 0)

        #     with open(audiofile_path+'.error','w') as f:
        #         f.write(repr(e))
        #     os.remove(audiofile_path+'.blocked')
