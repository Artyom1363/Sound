import unittest
import os
import json
from pydub import AudioSegment
from src.utils import cut_file
from src.exceptions import BadRequest


TEST_DATA_DIR = 'tests/data'
PATH_TO_BLEEPING = 'online_inference/bleeping_sounds/bleeping.mp3'

test_cutting_bad_cases = [
    [
        [
            {
                'start': -1.0,
                'end': 100.0,
                'filler': {
                    'empty': None
                }
            },
        ],
        'Boundaries must be: 0 <= left <= right'
    ],
    [
        [
            {
                'start': 1.0,
                'end': 0.5,
                'filler': {}
            },
        ],
        'Boundaries must be: 0 <= left <= right'
    ],
    [
        [
            {
                'start': 1.0,
                'end': 1.0,
            },
        ],
        "There is no filler in {'start': 1.0, 'end': 1.0}"
    ],
    [
        [
            {
                'start': 'str',
                'end': 1.0,
                'filler': None
            },
        ],
        'Boundaries must be numeric'
    ],
]

test_interview2 = [
    {'start': 0.7224080267558528, 'end': 1.5050167224080269, 'filler': 'empty'},
    {'start': 4.093645484949833, 'end': 4.494983277591974, 'filler': 'empty'},
    {'start': 11.773869346733669, 'end': 12.055276381909547, 'filler': 'empty'},
    {'start': 20.08028368794326, 'end': 20.160567375886526, 'filler': 'empty'},
    {'start': 20.381347517730497, 'end': 21.204255319148935, 'filler': 'empty'},
    {'start': 23.7331914893617, 'end': 24.275106382978723, 'filler': 'empty'},
    {'start': 13.32859296482412, 'end': 13.62421796482412, 'filler': 'empty'},
    {'start': 16.53773154362416, 'end': 16.86441904362416, 'filler': 'empty'}
]


class TestCutFile(unittest.TestCase):

    def setUp(self) -> None:
        self.source_audio_filepath = os.path.join(TEST_DATA_DIR, 'interview2.mp3')
        self.test_dirpath = os.path.join(TEST_DATA_DIR, 'tmp')


    def test_cross_fade(self):

        os.makedirs(self.test_dirpath, exist_ok=True)

        self.source_json_filepath = source_json = os.path.join(TEST_DATA_DIR, 'cross_at_start.json')

        json_file = open(self.source_json_filepath, "r")
        data = json.loads(json_file.read())

        processed_file = cut_file(self.test_dirpath, self.source_audio_filepath, data['redundants'], PATH_TO_BLEEPING)

        source_audio = AudioSegment.from_file(self.source_audio_filepath, format="mp3")
        processed_audio = AudioSegment.from_file(processed_file, format="mp3")

        # 0.5 1 -> 0.45 1.05 -> equal part will be from 1.05 + 450 = 1.5
        self.assertEqual(len(source_audio[1500:]), len(processed_audio[450:]))

    def test_interview2(self):
        os.makedirs(self.test_dirpath, exist_ok=True)

        processed_file = cut_file(self.test_dirpath, self.source_audio_filepath, test_interview2, PATH_TO_BLEEPING)
        # print(processed_file)

    def test_bad_json(self):
        for test_case in test_cutting_bad_cases:
            with self.assertRaises(BadRequest) as context:
                cut_file(self.test_dirpath, self.source_audio_filepath, test_case[0], PATH_TO_BLEEPING)
            self.assertEqual(test_case[1], str(context.exception))

        # with self.assertRaises(BadRequest) as context:
        #     cut_file(self.test_dirpath, self.source_audio_filepath, test_cutting_bad_cases[1], PATH_TO_BLEEPING)
        # self.assertEqual('Boundaries must be: 0 <= left <= right', str(context.exception))
        #
        # with self.assertRaises(BadRequest) as context:
        #     cut_file(self.test_dirpath, self.source_audio_filepath, test_cutting_bad_cases[2], PATH_TO_BLEEPING)
        # self.assertEqual("There is no filler in {'start': 1.0, 'end': 1.0}", str(context.exception))
        #
        # with self.assertRaises(BadRequest) as context:
        #     cut_file(self.test_dirpath, self.source_audio_filepath, test_cutting_bad_cases[3], PATH_TO_BLEEPING)
        # self.assertEqual("There is no filler in {'start': 1.0, 'end': 1.0}", str(context.exception))


if __name__ == '__main__':
    unittest.main()
