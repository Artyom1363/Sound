import unittest
import os
import json
from pydub import AudioSegment
from src.utils import cut_file
from src.exceptions import BadRequest


TEST_DATA_DIR = 'tests/data'
PATH_TO_BLEEPING = 'online_inference/bleeping_sounds/bleeping.mp3'

test_cross_at_start = [
    {
        "start": 0.5,
        "end": 1,
        "filler": {
            "empty": {
                "cross_fade": 3000
            }
        }
    }
]


test_fade_in_out_cases = [
    [
        {
            "start": 0.5,
            "end": 1,
            "filler": {
                "empty": {
                    "fade_in_out": {
                        'fade_in': 200,
                        'fade_out': 200,
                    }
                }
            }
        }
    ],
    [
        {
            "start": 0.5,
            "end": 1,
            "filler": {
                "empty": {
                    "fade_in_out": {
                        'fade_in': 1000,
                        'fade_out': 1,
                    }
                }
            }
        }
    ],

]

test_bleep = [
    {
        "start": 0.5,
        "end": 3,
        "filler": {
            'bleep': None
        }
    }
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

test_interview2_error = [
    {'start': 0.5324524365727598, 'end': 3.614523539704482, 'filler': 'empty'},
    {'start': 1.9541456797297305, 'end': 5.084845373423684, 'filler': 'empty'},
    {'start': 11.773869346733669, 'end': 12.055276381909547, 'filler': 'empty'},
    {'start': 20.08028368794326, 'end': 20.160567375886526, 'filler': 'empty'},
    {'start': 20.381347517730497, 'end': 21.204255319148935, 'filler': 'empty'},
    {'start': 23.7331914893617, 'end': 24.275106382978723, 'filler': 'empty'},
    {'start': 13.368583615388982, 'end': 13.534239001053182, 'filler': 'empty'},
    {'start': 16.64770583267753, 'end': 16.79443540513565, 'filler': 'empty'},
    {'start': 4.548936501753018, 'end': 6.35863030775224, 'filler': 'bleep'}
]


class TestCutFile(unittest.TestCase):

    def setUp(self) -> None:
        self.source_audio_filepath = os.path.join(TEST_DATA_DIR, 'interview2.mp3')
        self.test_dirpath = os.path.join(TEST_DATA_DIR, 'tmp')
        os.makedirs(self.test_dirpath, exist_ok=True)


    def test_cross_fade(self):

        processed_file = cut_file(self.test_dirpath, self.source_audio_filepath, test_cross_at_start, PATH_TO_BLEEPING)

        source_audio = AudioSegment.from_file(self.source_audio_filepath, format="mp3")
        processed_audio = AudioSegment.from_file(processed_file, format="mp3")

        # 0.5 1 -> 0.45 1.05 -> equal part will be from 1.05 + 450 = 1.5
        self.assertEqual(len(source_audio[1500:]), len(processed_audio[500:]))

    def test_interview2(self):

        processed_file = cut_file(self.test_dirpath, self.source_audio_filepath, test_interview2, PATH_TO_BLEEPING)
        processed_file = cut_file(self.test_dirpath, self.source_audio_filepath, test_interview2_error, PATH_TO_BLEEPING)

    def test_fade_in_out(self):

        processed_file = cut_file(self.test_dirpath, self.source_audio_filepath, test_fade_in_out_cases[0], PATH_TO_BLEEPING)

        source_audio = AudioSegment.from_file(self.source_audio_filepath, format="mp3")
        processed_audio = AudioSegment.from_file(processed_file, format="mp3")

        # self.assertEqual(source_audio[0:300].get_array_of_samples(), processed_audio[0:300].get_array_of_samples())
        self.assertEqual(len(source_audio[1200:]), len(processed_audio[700:]))

        processed_file = cut_file(self.test_dirpath, self.source_audio_filepath, test_fade_in_out_cases[1], PATH_TO_BLEEPING)

        source_audio = AudioSegment.from_file(self.source_audio_filepath, format="mp3")
        processed_audio = AudioSegment.from_file(processed_file, format="mp3")

        # self.assertEqual(len(source_audio[0:300]), len(processed_audio[0:300]))
        self.assertEqual(len(source_audio[1100:]), len(processed_audio[600:]))

    def test_bleep(self):

        processed_file = cut_file(self.test_dirpath, self.source_audio_filepath, test_bleep, PATH_TO_BLEEPING)

        source_audio = AudioSegment.from_file(self.source_audio_filepath, format="mp3")
        processed_audio = AudioSegment.from_file(processed_file, format="mp3")
        bleep = AudioSegment.from_file(PATH_TO_BLEEPING, format="mp3")
        bleep = bleep[1000:2000] * 5
        # 0.5 1 -> 0.45 1.05 -> equal part will be from 1.05 + 450 = 1.5
        self.assertEqual(len(source_audio), len(processed_audio))


    def test_none_redundants(self):
        processed_file = cut_file(self.test_dirpath, self.source_audio_filepath, None, PATH_TO_BLEEPING)

        source_audio = AudioSegment.from_file(self.source_audio_filepath, format="mp3")
        processed_audio = AudioSegment.from_file(processed_file, format="mp3")
        self.assertEqual(len(source_audio), len(processed_audio))

if __name__ == '__main__':
    unittest.main()
