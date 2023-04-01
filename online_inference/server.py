import os
import uvicorn
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

PATH_TO_PARASITE_WORDS_CLF_HEAD = 'online_inference/models/short_classif.pt'

@app.get("/")
def read_root():
    return "Parasite words classifier online"


@app.on_event("startup")
def loading_model():
    global model
    # model_path = os.getenv("PATH_TO_MODEL")
    model_path = PATH_TO_PARASITE_WORDS_CLF_HEAD
    if model_path is None:
        err = "PATH_TO_MODEL was not specified"
        logger.error(err)
        raise RuntimeError(err)

    model = WordClassifier(model_path) #load_model(model_path)


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
