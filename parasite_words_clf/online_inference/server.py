import os
import sys
import uvicorn
import nltk
import gdown
import torch
from fastapi import FastAPI
from typing import List
import logging
from pathlib import Path
from pydantic import BaseModel

from entities import WordClassifier
from src.entities import read_predict_pipeline_params
from src.app_logger import get_logger


app = FastAPI()

logger = get_logger(__name__)


PATH_TO_CONFIG = "configs/predict_config.yaml"

DIR_WITH_MODELS = 'online_inference/models'

MODEL_PATHS = {
    "короче": {
        "model_path": f'{DIR_WITH_MODELS}/short_classif.pt',
        "parasite_word_id": 80062,
    },
    "типа": {
        "model_path": f'{DIR_WITH_MODELS}/tipa_classif.pt',
        "parasite_word_id": 21798,
    }
}


class TextRequest(BaseModel):
    text: str


@app.get("/")
def read_root():
    return "Parasite words classifier online"


@app.on_event("startup")
def loading_model():
    nltk.download('punkt')
    params = read_predict_pipeline_params(PATH_TO_CONFIG)
    os.makedirs(DIR_WITH_MODELS, exist_ok=True)
    logger.info(f"params: {params}")
    gdown.download(id=params.id_short_clf_model, output=MODEL_PATHS['короче']['model_path'], quiet=False, fuzzy=True)
    gdown.download(id=params.id_tipa_clf_model, output=MODEL_PATHS['типа']['model_path'], quiet=False, fuzzy=True)

    global model
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    logger.info(f'device is {device}')
    model = WordClassifier(MODEL_PATHS, device)


@app.get("/health")
def read_health():
    return "Model is not ready " if model is None else "Model is ready"


@app.post("/predict/", response_model=List[int])
def predict(request: TextRequest):
    logger.info(f"Text of request: {request.text}")
    return model.predict(request.text)


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=os.getenv("PORT", 8000))
