import unittest
from src.utils.cutting import fill_fade_settings
from src.utils.cutting import preprocess_redundants


DEFAULT_FADE_IN = 150
DEFAULT_FADE_OUT = 150
DEFAULT_CROSS_FADE = 200


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


class TestFillFadeSettings(unittest.TestCase):

    def test_empty_cross_fade_good_cases(self):
        for case in test_empty_cross_fade_good_cases:
            self.assertEqual(fill_fade_settings(case[0]), case[1])

    def test_empty_in_out_good_cases(self):
        for case in test_empty_in_out_good_cases:
            self.assertEqual(fill_fade_settings(case[0]), case[1])

    def test_bleep_good_cases(self):
        for case in test_bleep_good_cases:
            self.assertEqual(fill_fade_settings(case[0]), case[1])


class TestOverlappedSettings(unittest.TestCase):

    def test_overlapped_cases(self):
        for case in test_overlapped_cases:
            self.assertEqual(preprocess_redundants(case[0]), case[1])


if __name__ == '__main__':
    unittest.main()
