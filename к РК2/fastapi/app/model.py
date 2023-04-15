from df.enhance import enhance, init_df, load_audio, save_audio
from df.utils import download_file
import whisper 
import whisperx
# from stable_whisper import modify_model
import os
from datetime import datetime
import multiprocessing as mp
import json
STORAGE = "./content"
DEVICE = 'cpu'
def add_timestamp(filename:str):
    return filename[:filename.rfind('.')] +'_'+datetime.now().strftime("%m-%d-%Y_%H.%M.%S")+filename[filename.rfind('.'):]
    
def init_storage_path():
    """
    Инициализация папки с контентом, куда всё будет сохраняться
    """
    
    if not os.path.exists(STORAGE):
        os.mkdir(STORAGE)
    
    return STORAGE
    


def get_timestamps_and_profanity(result_dict):
    ban_words = ['еб','сука','сук',"блять","бля","пидор","гей","мудак","муд","говно","говн","уебище","уёби","еба","ёба", "жопа", "еблан", "долбаёб","далбаёб","долбаеб","далбаеб","жопа","зад","дроч","ху","ублюдок","пиздец","пизда","пиз","еба"]

    
    words = []
    
    for word in result_dict:
        is_profanity = False
        if word['text'].lower() in ban_words:
            is_profanity = True
        else:
            for ban in ban_words:
                if ban in word['text'].lower():
                    is_profanity = True
                    break
        temp_word = {
            'word':word['text'],
            'start':word['start'],
            'end':word['end'],
            'is_profanity':is_profanity,
            'tokens':[1],
            'probability':1.0                
        }
        words.append(temp_word)

    return words



def process_init():
    DFmodel, df_state, _ = init_df(post_filter = False,config_allow_defaults = True)
    whisper_model = whisper.load_model('small',device = DEVICE)
    #modify_model(whisper_model)
    return whisper_model, DFmodel, df_state

def proccess_audio(audio_path,whisper_model,deepfilter_model,df_state):
    #возвращает audio, text и таймштампы с матами
    
    audio, _ = load_audio(audio_path, sr=df_state.sr())#df_state.sr() - частота дискретизации
    
    enhanced = enhance(deepfilter_model, df_state, audio)
    enhanced_audio_path = audio_path[:audio_path.rfind('.')]+"_enhanced.wav"
    save_audio(enhanced_audio_path,enhanced, df_state.sr())
    


    
    result = whisper_model.transcribe(enhanced_audio_path, language='ru')

    model_a, metadata = whisperx.load_align_model(language_code='ru', device=DEVICE)

    # align whisper output
    result_aligned = whisperx.align(result["segments"], model_a, metadata, enhanced_audio_path, DEVICE)

    # result_dict = result.to_dict() 
    text = result["text"]
    words = get_timestamps_and_profanity(result_aligned['word_segments'])
    
    return enhanced_audio_path, text, words

def worker_ant(queue:mp.Queue, err_queue:mp.Queue):
    whisper_model, DFmodel, df_state = process_init()
    while True:
        audiofile_path = queue.get()
        # try:
            
            
        open(audiofile_path+'.blocked','wb')
        enhanced_audio_path, text, words =proccess_audio(audiofile_path,whisper_model, DFmodel, df_state)  
        response_json ={
            "text":text,
            "words":words
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

            

