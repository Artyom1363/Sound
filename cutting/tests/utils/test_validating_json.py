import unittest
from src.utils.cutting import fill_fade_settings
from src.utils.cutting import preprocess_redundants
from src.exceptions import BadRequest


DEFAULT_FADE_IN = 150
DEFAULT_FADE_OUT = 150
DEFAULT_CROSS_FADE = 200


test_json_bad_cases = [
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

test_filler_bad_cases = [
    [
        {
            'empty':{
                'fade_in_out':{
                    'fade_in': -1,
                    'fade_out': 1,
                }
            }
        },
        "Invalid fade_in in {'fade_in': -1, 'fade_out': 1}"
    ],
    [
        {
            'empty': {
                'fade_in_out':{
                    'fade_in': 1,
                    'fade_out': -1,
                }
            }
        },
        "Invalid fade_out in {'fade_in': 1, 'fade_out': -1}"
    ],
    [
        {
            'empty': {
                'fade_in_out':{
                    'fade_in': 'str',
                    'fade_out': 1,
                }
            }
        },
        "Invalid fade_in in {'fade_in': 'str', 'fade_out': 1}"
    ],
]

test_empty_cross_fade_good_cases = [
    [
        {
            'empty': None
        },
        {
            'empty': {
                'cross_fade': DEFAULT_CROSS_FADE
            }
        }
    ],
    [
        {
            'empty': {}
        },
        {
            'empty': {
                'cross_fade': DEFAULT_CROSS_FADE
            }
        }
    ],
    [
        {
            'empty': {
                'cross_fade': None
            }
        },
        {
            'empty': {
                'cross_fade': DEFAULT_CROSS_FADE
            }
        }
    ],
    [
        {
            'empty': {
                'cross_fade': 3000
            }
        },
        {
            'empty': {
                'cross_fade': 3000
            }
        }
    ],
    [
        'empty',
        {
            'empty': {
                'cross_fade': DEFAULT_CROSS_FADE
            }
        }
    ],
]

test_empty_in_out_good_cases = [
    [
        {
            'empty': {
                'fade_in_out': None
            }
        },
        {
            'empty': {
                'fade_in_out': {
                    'fade_in': DEFAULT_FADE_IN,
                    'fade_out': DEFAULT_FADE_OUT
                }
            }
        }
    ],
    [
        {
            'empty': {
                'fade_in_out': {}
            }
        },
        {
            'empty': {
                'fade_in_out': {
                    'fade_in': DEFAULT_FADE_IN,
                    'fade_out': DEFAULT_FADE_OUT
                }
            }
        }
    ],
    [
        {
            'empty': {
                'fade_in_out': {
                    'fade_in': 1000,
                }
            }
        },
        {
            'empty': {
                'fade_in_out': {
                    'fade_in': 1000,
                    'fade_out': DEFAULT_FADE_OUT
                }
            }
        }
    ],
    [
        {
            'empty': {
                'fade_in_out': {
                    'fade_out': 1000,
                }
            }
        },
        {
            'empty': {
                'fade_in_out': {
                    'fade_in': DEFAULT_FADE_IN,
                    'fade_out': 1000
                }
            }
        }
    ],
    [
        {
            'empty': {
                'fade_in_out': {
                    'fade_in': 10.5,
                    'fade_out': 1000
                }
            }
        },
        {
            'empty': {
                'fade_in_out': {
                    'fade_in': 10.5,
                    'fade_out': 1000
                }
            }
        }
    ],
    [
        {
            'empty': {
                'fade_in_out': {
                    'fade_in': None,
                    'fade_out': None
                }
            }
        },
        {
            'empty': {
                'fade_in_out': {
                    'fade_in': DEFAULT_FADE_IN,
                    'fade_out': DEFAULT_FADE_OUT
                }
            }
        }
    ],
]

test_bleep_good_cases = [
    [
        {
            'bleep': None
        },
        {
            'bleep': {}
        },
    ],
    [
        {
            'bleep': {}
        },
        {
            'bleep': {}
        },
    ],
    [
        'bleep',
        {
            'bleep': {}
        },
    ],
]

test_overlapped_cases = [
    [
        [
            {
                'start': 1,
                'end': 2,
                'filler': {
                    'empty': {
                        'cross_fade': 2000
                    }
                }
            },
            {
                'start': 1.5,
                'end': 3,
                'filler': {
                    'empty': {
                        'fade_in_out': None
                    }
                }
            }
        ],
        [
            {
                'start': 1,
                'end': 3,
                'filler': {
                    'empty': {
                        'cross_fade': 2000
                    }
                }
            },
        ],
    ],
    [
        [
            {
                'start': 1,
                'end': 2,
                'filler': {
                    'empty': {
                        'cross_fade': 2000
                    }
                }
            },
            {
                'start': 1.5,
                'end': 3,
                'filler': {
                    'bleep': None
                }
            }
        ],
        [
            {
                'start': 1,
                'end': 2,
                'filler': {
                    'empty': {
                        'fade_in_out': {
                            'fade_in': 0,
                            'fade_out': 0
                        }
                    }
                }
            },
            {
                'start': 2,
                'end': 3,
                'filler': {
                    'bleep': {}
                }
            },
        ],
    ],
    [
        [
            {
                'start': 1,
                'end': 2,
                'filler': {
                    'bleep': None
                }
            },
            {
                'start': 1.5,
                'end': 3,
                'filler': {
                    'empty': {
                        'cross_fade': 2000
                    }
                }
            }
        ],
        [
            {
                'start': 1,
                'end': 2,
                'filler': {
                    'bleep': {}
                }
            },
            {
                'start': 2,
                'end': 3,
                'filler': {
                    'empty': {
                        'fade_in_out': {
                            'fade_in': 0,
                            'fade_out': 0
                        }
                    }
                }
            },
        ],
    ],
    [
        [
            {
                'start': 1,
                'end': 3.5,
                'filler': {
                    'empty': {
                        'cross_fade': 2000
                    }
                }
            },
            {
                'start': 1.5,
                'end': 3,
                'filler': {
                    'empty': {
                        'fade_in_out': None
                    }
                }
            }
        ],
        [
            {
                'start': 1,
                'end': 3.5,
                'filler': {
                    'empty': {
                        'cross_fade': 2000
                    }
                }
            },
        ],
    ],
]


class TestJsonValidation(unittest.TestCase):

    def test_json_bad_cases(self):
        for test_case in test_json_bad_cases:
            with self.assertRaises(BadRequest) as context:
                preprocess_redundants(test_case[0])
            self.assertEqual(test_case[1], str(context.exception))

    def test_empty_cross_fade_good_cases(self):
        for case in test_empty_cross_fade_good_cases:
            if fill_fade_settings(case[0]) != case[1]:
                print(f"NOt equal: {fill_fade_settings(case[0])}\t{case[0]}")
            self.assertEqual(fill_fade_settings(case[0]), case[1])


    def test_empty_in_out_good_cases(self):
        for case in test_empty_in_out_good_cases:
            self.assertEqual(fill_fade_settings(case[0]), case[1])

    def test_bleep_good_cases(self):
        for case in test_bleep_good_cases:
            self.assertEqual(fill_fade_settings(case[0]), case[1])

    def test_filler_bad_cases(self):
        for test_case in test_filler_bad_cases:
            with self.assertRaises(BadRequest) as context:
                fill_fade_settings(test_case[0])
            self.assertEqual(test_case[1], str(context.exception))


class TestOverlappedSettings(unittest.TestCase):

    def test_overlapped_cases(self):
        for case in test_overlapped_cases:
            self.assertEqual(preprocess_redundants(case[0]), case[1])


if __name__ == '__main__':
    unittest.main()
