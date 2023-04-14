import os
import time
import json
from typing import Tuple, List
import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
import logging
import aiofiles
# from src.utils import cut_file, speech_file_to_array_fn, ffmpeg_convert, librosa_convert
from src.utils import cut_file, format_file

SAMPLING_RATE = 16000
app = FastAPI()

model_name_or_path = "jonatasgrosman/wav2vec2-large-xlsr-53-russian"
pooling_mode = "mean"
label_list = ['Breath', 'Laughter', 'Music', 'Uh', 'Um', 'Words']
num_labels = 6

HOST = "95.64.151.158"
PORT = "8000"
URL = f"http://{HOST}:{PORT}"

logger = logging.getLogger(__name__)


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
    # fragments_path_mp3 = os.path.join(query_dir, "files")
    os.makedirs(query_dir)
    # os.mkdir(fragments_path_mp3)
    return query_dir


@app.get("/")
def read_root():
    return "Cutting server online"


@app.on_event("startup")
def loading_model():
    pass


@app.get("/health")
def read_health():
    return "Service is not ready" if model is None else "Service is ready"


@app.post("/cut/")
async def predict(response: FileResponse, request: List[UploadFile] = File(..., ext_whitelist=["json", "mp3"])):
    # print()
    files = {}
    extensions = ['.json', '.mp3']
    for file in request:
        print(file.content_type)
        filename, file_extension = os.path.splitext(file.filename)
        if file_extension in extensions and file_extension not in files.keys():
            files[file_extension] = file
        else:
            response.status_code = 404
            return f"Bad files! We need one json and one mp3 file"

    for ext in extensions:
        if ext not in files.keys():
            response.status_code = 404
            return f"have not {ext} file"

    cur_dir = os.path.dirname(os.path.abspath(__file__))
    data_directory = os.path.join(cur_dir, 'data')
    # print(data_directory)
    query_dir = create_query_paths(data_directory)
    filename_mp3 = os.path.join(query_dir, f'src.mp3')
    filename_json = os.path.join(query_dir, f'src.json')

    async with aiofiles.open(filename_json, 'wb') as out_file:
        content = await files['.json'].read()  # async read
        await out_file.write(content)  # async write

    async with aiofiles.open(filename_mp3, 'wb') as out_file:
        content = await files['.mp3'].read()  # async read
        await out_file.write(content)  # async write

    json_file = open(filename_json, "r")
    data = json.loads(json_file.read())
    # print("DEBUG! DATA:", data)

    out_file = cut_file(query_dir, 'src.mp3', data['redundants'])
    # format_file(query_dir, 'src.mp3')
    print("DEBUG! OUTPUT FILE: ", out_file)

    return FileResponse(out_file)


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=os.getenv("PORT", 8002))
