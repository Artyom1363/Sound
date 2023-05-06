from df.enhance import enhance, init_df, save_audio
from app.backend_tools import read_config
from faster_whisper import WhisperModel
import whisperx
import torchaudio
config = read_config()


def process_init():
    """инициализация worker'а

    Returns:
        необходимые атрибуты
    """
    DFmodel, df_state, _ = init_df(
        post_filter=True, config_allow_defaults=True)
    whisper_model = WhisperModel(
        config["model_size"], device=config['DEVICE'], compute_type=config["compute_type"])
    profanity_set = get_profanity_set(config["profanity_file_path"])
    model_a, metadata = whisperx.load_align_model(
        language_code=config['language_code'], device=config['DEVICE'])

    return whisper_model, DFmodel, df_state, profanity_set, model_a, metadata


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


def proccess_audio(audio_path, whisper_model, deepfilter_model, df_state, profanity_set, model_a, metadata):
    # возвращает audio, text и таймштампы с матами
    # df_state.sr() - частота дискретизации
    audio, sound_rate = torchaudio.load(audio_path)
    if config["DEVICE"] == "cuda":
        audio = audio.cuda()
    if sound_rate != df_state.sr():
        audio = torchaudio.functional.resample(
            audio, sound_rate, df_state.sr(), lowpass_filter_width=128)

    enhanced = enhance(deepfilter_model, df_state, audio)
    enhanced_audio_path = audio_path[:audio_path.rfind('.')]+"_enhanced.mp3"
    save_audio(enhanced_audio_path, enhanced, df_state.sr())

    result = whisper_model.transcribe(enhanced_audio_path, language=config["language_code"])

    # align whisper output
    result_aligned = whisperx.align(
        result["segments"], model_a, metadata, enhanced_audio_path, config["DEVICE"])

    # result_dict = result.to_dict()
    text = result["text"]
    words = get_timestamps_and_profanity(
        result_aligned['word_segments'], profanity_set)

    return enhanced_audio_path, text, words
