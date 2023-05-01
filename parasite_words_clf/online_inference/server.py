import os
import sys
import uvicorn
import nltk
import gdown
import torch
from fastapi import FastAPI
import logging
from pathlib import Path

from entities import WordClassifier
from src.app_logger import get_logger


app = FastAPI()

logger = get_logger(__name__)


ID_SHORT_CLF_MODEL = '1b2s8fZESNf6idt6csRhoVmVr8m_VRCeJ'
ID_TIPA_CLF_MODEL = '1E3yxQsUQoGbk-_8eCsqc4l7Gb8_3SwqT'

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


@app.get("/")
def read_root():
    return "Parasite words classifier online"


@app.on_event("startup")
def loading_model():
    nltk.download('punkt')

    os.makedirs(DIR_WITH_MODELS, exist_ok=True)
    gdown.download(id=ID_SHORT_CLF_MODEL, output=MODEL_PATHS['короче']['model_path'], quiet=False, fuzzy=True)
    gdown.download(id=ID_TIPA_CLF_MODEL, output=MODEL_PATHS['типа']['model_path'], quiet=False, fuzzy=True)

    global model
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    logger.info(f'device is {device}')
    model = WordClassifier(MODEL_PATHS, device)


@app.get("/health")
def read_health():
    return "Model is not ready " if model is None else "Model is ready"


@app.get("/predict/", response_model=list[int])
def predict(request: str):
    return model.predict(request)


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=os.getenv("PORT", 8000))
