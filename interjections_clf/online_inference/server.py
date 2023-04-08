import os
import time
import json
import torch
from typing import Tuple, List
import requests
import uvicorn
from fastapi import FastAPI, Response
import logging
from src.utils import cut_file, speech_file_to_array_fn, ffmpeg_convert, librosa_convert
from src.models import Wav2Vec2ForSpeechClassification
from transformers import AutoConfig, Wav2Vec2Processor


app = FastAPI()

model_name_or_path = "jonatasgrosman/wav2vec2-large-xlsr-53-russian"
pooling_mode = "mean"
label_list = ['Breath', 'Laughter', 'Music', 'Uh', 'Um', 'Words']
num_labels = 6


HOST = "95.64.151.158"
PORT = "8000"
URL = f"http://{HOST}:{PORT}"

logger = logging.getLogger(__name__)

PATH_TO_MODEL = 'online_inference/models/interjections_clf_cpu.pt'


def create_query_paths(data_directory: str) -> Tuple[str, str]:
    """
    This function creates working dirs for handling query
    1. data_directory/gaps_mp3
    2. data_directory/gaps_wav
    :return: query_dir
    """
    timestr = time.strftime("%Y-%m-%d-%H-%M-%S")
    print("cur_dir is: ", data_directory)

    query_dir = os.path.join(data_directory, timestr)
    fragments_path_mp3 = os.path.join(query_dir, "gaps_mp3")
    fragments_path_wav = os.path.join(query_dir, "gaps_wav")
    os.makedirs(query_dir)
    os.mkdir(fragments_path_mp3)
    os.mkdir(fragments_path_wav)
    return query_dir


def slice_the_voids(query_dir: str) -> List[Tuple[float, float, str]]:
    '''
    :param query_dir: path to query dir
    :return: List[Tuple[start timestamp, end timestamp, path to file]]
    '''
    threshold = 0.2
    gaps = []
    start_gap, end_gap = 0, 0
    source_audio_file_path = os.path.join(query_dir, 'source.mp3')
    source_text_info_file_path = os.path.join(query_dir, 'text_info.json')
    gaps_mp3_dir_path = os.path.join(query_dir, 'gaps_mp3')
    gaps_wav_dir_path = os.path.join(query_dir, 'gaps_wav')
    json_file = open(source_text_info_file_path)
    data_str = json.load(json_file)
    data = json.loads(data_str)
    data = sorted(data['words'], key=lambda word: word['start'])

    for idx, word in enumerate(data):

        end_gap = word['start']

        if end_gap - start_gap < threshold:
            start_gap = word['end']
            continue

        # gaps.append((start_gap, end_gap))
        gap_mp3_file_path = os.path.join(gaps_mp3_dir_path, f'{idx}.mp3')
        gap_wav_file_path = os.path.join(gaps_wav_dir_path, f'{idx}.wav')

        gaps.append((start_gap, end_gap, gap_wav_file_path))

        cut_file(source_audio_file_path, gap_mp3_file_path, start_gap, end_gap)
        # ffmpeg_convert(gap_mp3_file_path, gap_wav_file_path)
        librosa_convert(gap_mp3_file_path, gap_wav_file_path)

        start_gap = word['end']

    return gaps


def predict_model(speech_array, model, processor, device):
    features = processor(speech_array, sampling_rate=processor.feature_extractor.sampling_rate, return_tensors="pt",
                         padding=True, return_attention_mask=True)

    input_values = features.input_values.to(device)
    attention_mask = features.attention_mask.to(device)

    with torch.no_grad():
        logits = model(input_values, attention_mask).logits  # attention_mask

    pred_ids = torch.argmax(logits, dim=-1).detach().cpu().numpy()
    return pred_ids


@app.get("/")
def read_root():
    return "Interjections classifier online"


@app.on_event("startup")
def loading_model():
    global model
    global processor
    global device
    device = 'cpu'

    config = AutoConfig.from_pretrained(
        model_name_or_path,
        num_labels=num_labels,
        label2id={label: i for i, label in enumerate(label_list)},
        id2label={i: label for i, label in enumerate(label_list)},
        finetuning_task="wav2vec2_clf",
    )
    setattr(config, 'pooling_mode', pooling_mode)

    model = Wav2Vec2ForSpeechClassification.from_pretrained(
        model_name_or_path,
        config=config,
    )

    model.load_state_dict(torch.load(PATH_TO_MODEL))
    processor = Wav2Vec2Processor.from_pretrained(model_name_or_path)
    # model = 1
    # model_path = PATH_TO_PARASITE_WORDS_CLF_HEAD
    # if model_path is None:
    #     err = "PATH_TO_MODEL was not specified"
    #     logger.error(err)
    #     raise RuntimeError(err)
    #
    # model = WordClassifier(MODEL_PATHS) #load_model(model_path)


@app.get("/health")
def read_health():
    return "Model is not ready " if model is None else "Model is ready"


@app.get("/predict/")
def predict(resp: Response, request: int):
    file_id = request
    req_src_file = URL + f"/get_file_by_id?file_id={str(file_id)}"
    req_text_file = URL + f"/get_text_by_id?file_id={str(file_id)}"
    # print("req:", req)
    response = requests.get(req_src_file)
    if response.status_code != 200:
        return []
    print("Source file response is OK!")
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    data_directory = os.path.join(cur_dir, 'data')
    # print(data_directory)
    query_dir = create_query_paths(data_directory)
    # print("os.path.join(query_dir, 'source.mp3'): ", os.path.join(query_dir, 'source.mp3'))
    with open(os.path.join(query_dir, 'source.mp3'), 'wb') as file:
        file.write(response.content)

    response = requests.get(req_text_file)
    if response.status_code != 200:
        return []

    print("JSON response is OK!")
    # data_directory = os.path.dirname(os.path.abspath(__file__))
    # print(data_directory)
    # file_dir, file_path = create_query_paths(data_directory)
    text_info_filepath = os.path.join(query_dir, 'text_info.json')
    with open(text_info_filepath, 'wb') as file:
        file.write(response.content)

    # data = json.loads()
    # print(data)
    gaps_info = slice_the_voids(query_dir)
    # print("GAPS_INFO: \n\n\n\n\n\n", gaps_info)
    gaps_ans = []

    for idx, gap in enumerate(gaps_info):
        # print("GAPS_INFO: \n\n\n\n\n\n", gaps_info)
        print("GAP: ", gap)
        speech_arr = speech_file_to_array_fn(gap[2], processor)
        pred_label = predict_model(speech_arr, model, processor, device)
        print(idx, pred_label)
        record = {}
        record['start'] = gap[0]
        record['end'] = gap[1]
        record['label'] = 'um'
        if pred_label in [3, 4]:
            gaps_ans.append(record)

    resp.status_code = 200
    return json.dumps(gaps_ans)
    # return make_predict(request.data, request.features, model)


if __name__ == "__main__":

    uvicorn.run("server:app", host="0.0.0.0", port=os.getenv("PORT", 8001))
