import os
import uvicorn
import nltk
from fastapi import FastAPI
import logging
from pathlib import Path

import sys

from entities import (
    WordClassifier,
    # make_predict,
    # load_model,
)

app = FastAPI()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

logging_handler = logging.StreamHandler()
logging_handler.setLevel(logging.INFO)
logger.addHandler(logging_handler)

PATH_TO_PARASITE_WORDS_CLF_HEAD = 'online_inference/models/short_classif.pt'

MODEL_PATHS = {
    "короче": {
        "model_path": 'online_inference/models/short_classif.pt',
        "parasite_word_id": 80062,
    },
    "типа": {
        "model_path": 'online_inference/models/tipa_classif.pt',
        "parasite_word_id": 21798,
    }
}


@app.get("/")
def read_root():
    return "Parasite words classifier online"


@app.on_event("startup")
def loading_model():
    nltk.download('punkt')
    global model
    # model_path = os.getenv("PATH_TO_MODEL")
    model_path = PATH_TO_PARASITE_WORDS_CLF_HEAD
    if model_path is None:
        err = "PATH_TO_MODEL was not specified"
        logger.error(err)
        raise RuntimeError(err)

    model = WordClassifier(MODEL_PATHS) #load_model(model_path)


@app.get("/health")
def read_health():
    return "Model is not ready " if model is None else "Model is ready"


@app.get("/predict/", response_model=list[int])
def predict(request: str):
    return model.classify(request)
    # return make_predict(request.data, request.features, model)


if __name__ == "__main__":
    # print(sys.path)
    # current_dir = Path(__file__)
    # print(current_dir)
    uvicorn.run("server:app", host="0.0.0.0", port=os.getenv("PORT", 8000))
