import unittest
import os
import json
from pydub import AudioSegment
from src.utils import cut_file


TEST_DATA_DIR = 'tests/data'
PATH_TO_BLEEPING = 'online_inference/bleeping_sounds/bleeping.mp3'


class TestCutFile(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def test_cross_fade(self):
        test_dirpath = os.path.join(TEST_DATA_DIR, 'tmp')
        os.makedirs(test_dirpath, exist_ok=True)

        source_audio = os.path.join(TEST_DATA_DIR, 'interview2.mp3')
        source_json = os.path.join(TEST_DATA_DIR, 'cross_at_start.json')

        json_file = open(source_json, "r")
        data = json.loads(json_file.read())
        print(f"DAta: {data}")

        processed_file = cut_file(test_dirpath, source_audio, data['redundants'], PATH_TO_BLEEPING)

        source_audio = AudioSegment.from_file(source_audio, format="mp3")
        processed_audio = AudioSegment.from_file(processed_file, format="mp3")

        print(f"len is: {len(source_audio)}")
        # 0.5 1 -> 0.45 1.05 -> equal part will be from 1.05 + 450 = 1.5
        self.assertEqual(len(source_audio[1500:]), len(processed_audio[450:]))


if __name__ == '__main__':
    unittest.main()
