from threading import Thread
from typing import Annotated
from fastapi import FastAPI,  UploadFile, Response
from fastapi.responses import FileResponse
import multiprocessing as mp
import os
from app.model import init_storage_path, add_timestamp, worker_ant
app = FastAPI()


mp_ctx = mp.get_context('spawn')

audio_file_tasks_quque = mp_ctx.Queue()
errors_from_process = mp_ctx.Queue()
p = mp_ctx.Process(target=worker_ant, args=(audio_file_tasks_quque,errors_from_process,))
p.start()
model_ready = False
storage_path = ""
id_to_filename = {}
id_counter = 0


@app.on_event("startup")
def startup_model():
    global model_ready, storage_path
    storage_path = init_storage_path()

    model_ready = True


@app.get("/ready")
def health(response: Response):
    response.status_code = 200 if model_ready else 503
    return model_ready


@app.get("/")
def default():
    return {"Name": "speech_to_text",
            'Author': 'Kerimov Nuraddin'}


@app.post("/transcribe")
async def transcribe(file: UploadFile, response: Response):
    global id_counter
    if not model_ready:
        response.status_code = 503
        return "model not ready!"

    if file.filename[file.filename.rfind("."):] != ".mp3":
        response.status_code = 503
        return "wrong file format, expected .mp3"

    audio_path = storage_path+'/'+add_timestamp(file.filename)
    with open(audio_path, "wb") as f:
        f.write(file.file.read())
    id_to_filename[id_counter] = audio_path
    audio_file_tasks_quque.put(audio_path)
    id_counter += 1
    response.status_code = 200
    return {"file_id": id_counter-1}


@app.get("/get_file_by_id")
async def get_file_by_id(response: Response, file_id: int = 0,):

    if not model_ready:
        response.status_code = 503
        return "model not ready!"
    if file_id not in id_to_filename:
        response.status_code = 404
        return "file_id not found!"

    response.status_code = 200

    return FileResponse(id_to_filename[file_id])


@app.get("/get_data_by_id")
async def get_data_by_id(response: Response, file_id: int = 0,):

    if not model_ready:
        response.status_code = 503
        return "model not ready!"
    if file_id not in id_to_filename:
        response.status_code = 404
        return "file_id not found!"
    
    
    audio_path = id_to_filename[file_id]
    
    if os.path.exists(audio_path+'.error'):
        response.status_code = 503
        with open(audio_path+'.error','r') as f:
            err = f.read()
        return "model inherence error! " + err
    
    
    enhansed_path = audio_path[:audio_path.rfind('.')]+"_enhanced.wav"
    if (not os.path.exists(audio_path+'.blocked')) and os.path.exists(enhansed_path):
        response.status_code = 200
        return FileResponse(enhansed_path)
    response.status_code = 418
    return "file not ready!"

@app.get("/get_text_by_id")
async def get_text_by_id(response: Response, file_id: int = 0,):

    if not model_ready:
        response.status_code = 503
        return "model not ready!"
    if file_id not in id_to_filename:
        response.status_code = 404
        return "file_id not found!"
    
    audio_path = id_to_filename[file_id]
    
    if os.path.exists(audio_path+'.error'):
        response.status_code = 503
        with open(audio_path+'.error','r') as f:
            err = f.read()
        return "model inherence error! " + err

    json_path = audio_path+'.json'
    if (not os.path.exists(audio_path+'.blocked')) and os.path.exists(json_path):
        response.status_code = 200
        answer = ""
        with open(json_path,"r", encoding='utf8') as f:
            answer = f.read()
        return answer
    response.status_code = 418
    return "file not ready!"