from df.enhance import enhance, init_df
from app.backend_tools import read_config
import whisperx
import torchaudio
import ffmpeg
import torch
config = read_config()


def process_init():
    """инициализация worker'а

    Returns:
        необходимые атрибуты
    """
    DFmodel, df_state, _ = init_df(
        post_filter=True, config_allow_defaults=True)
    # whisper_model = WhisperModel(
    #     )
    whisper_model = whisperx.load_model(config["model_size"], device=config['DEVICE'], compute_type=config["compute_type"],language = 'ru')
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
    audio_path_wav_48kHz = audio_path[:audio_path.rfind('.')]+'_48kHz.wav'
    process1 = (
    ffmpeg
    .input(audio_path)
    .output(audio_path_wav_48kHz, **{'ar': '48000',})
    .run()
    )


    audio, sound_rate = torchaudio.load(audio_path_wav_48kHz)
    enhanced_list = []
    audio = audio.contiguous()
    batch_size = config['filter_batch_size']
    for batch in range(audio.shape[1]//batch_size):
        enhanced_list.append(enhance(deepfilter_model, df_state, audio[:,batch_size*batch:batch_size*(batch+1)]))
    enhanced_list.append(enhance(deepfilter_model, df_state, audio[:,batch_size*(audio.shape[1]//batch_size):]).cpu())
    enhanced_audio_path = audio_path[:audio_path.rfind('.')]+"_enhanced.wav"
    torchaudio.save(enhanced_audio_path, torch.concat(enhanced_list,dim=1), df_state.sr())
    for tensor in enhanced_list:
        del tensor
    audio_path_mp3_16kHz = enhanced_audio_path[:enhanced_audio_path.rfind('.')]+'_16kHz.mp3'
    process2 = (
    ffmpeg
    .input(enhanced_audio_path)
    .output(audio_path_mp3_16kHz, **{'ar': '48000',})
    .run()
    )

    
    audio, sound_rate = torchaudio.load(audio_path_mp3_16kHz)
       
    audio = whisperx.load_audio(audio_path_mp3_16kHz)
    result = whisper_model.transcribe(audio, batch_size=32)


    result_aligned = whisperx.align(result["segments"], model_a, metadata, audio, config["DEVICE"])
    words = get_timestamps_and_profanity(
        result_aligned['word_segments'], profanity_set)
    text = ''
    for seg in result["segments"]:
        text += seg['text']
    return enhanced_audio_path, text, words
