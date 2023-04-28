import os
import time
import json
from typing import Tuple, List
import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
import logging
import aiofiles
from src.utils import cut_file
from src import app_logger

BLEEPING_SOUNDS_DIR = 'bleeping_sounds'

app = FastAPI()
logger = app_logger.get_logger(__name__)


def create_query_paths(data_directory: str) -> Tuple[str, str]:
    """
    This function creates working dirs for handling query
    1. data_directory/gaps_mp3
    2. data_directory/gaps_wav
    :return: query_dir
    """

    timestr = time.strftime("%Y-%m-%d-%H-%M-%S")
    logger.debug(f'cur_dir is: {data_directory}')

    query_dir = os.path.join(data_directory, timestr)
    os.makedirs(query_dir)
    return query_dir


@app.get("/")
def read_root():
    return "Cutting server online"


@app.on_event("startup")
def init():
    pass


@app.get("/health")
def read_health():
    return "Service is ready"


@app.post("/cut/")
async def predict(response: FileResponse, request: List[UploadFile] = File(..., ext_whitelist=["json", "mp3"])):
    files = {}
    extensions = ['.json', '.mp3']
    for file in request:
        logger.debug(f'got file: {file.content_type}')
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

    query_dir = create_query_paths(data_directory)
    filename_mp3 = os.path.join(query_dir, f'src.mp3')
    filename_json = os.path.join(query_dir, f'src.json')
    filename_beep = os.path.join(cur_dir, BLEEPING_SOUNDS_DIR, f'bleeping.mp3')

    async with aiofiles.open(filename_json, 'wb') as out_file:
        content = await files['.json'].read()  # async read
        await out_file.write(content)  # async write

    async with aiofiles.open(filename_mp3, 'wb') as out_file:
        content = await files['.mp3'].read()  # async read
        await out_file.write(content)  # async write

    json_file = open(filename_json, "r")
    data = json.loads(json_file.read())

    # src_file = os.path.join(dir_path, file_name)
    out_file = cut_file(query_dir, filename_mp3, data['redundants'], filename_beep)

    logger.debug(f'OUTPUT FILE: {out_file}')

    return FileResponse(out_file)


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=os.getenv("PORT", 8002))
