import torchaudio
import librosa
import numpy as np


def speech_file_to_array_fn(file_path, processor):
    speech_array, sampling_rate = torchaudio.load(file_path)
    speech_array = speech_array.squeeze().numpy()
    speech_array = librosa.resample(np.asarray(speech_array), sampling_rate, processor.feature_extractor.sampling_rate)
    return speech_array
