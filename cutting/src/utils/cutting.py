from pydub import AudioSegment
import logging
import os
import numbers
from src import app_logger
from src.exceptions import BadRequest

logger = app_logger.get_logger(__name__)
DEFAULT_FADE_IN = 150
DEFAULT_FADE_OUT = 150
DEFAULT_CROSS_FADE = 200


def fill_fade_settings(redundant_filler: dict):
    res_filler = {}
    logger.debug(f"redundant_filler in fill_fade_settings: {redundant_filler}")
    # logger.debug(f"redundant_filler['emplty']: {redundant_filler['empty']}")
    if type(redundant_filler) == dict:
        if 'empty' in redundant_filler:
            res_filler['empty'] = {}
            if redundant_filler['empty'] is None:
                redundant_filler['empty'] = {}

            if not isinstance(redundant_filler['empty'], dict):
                logger.debug(f"Invalid object type in empty: {redundant_filler['empty']} ")
                raise BadRequest(f"Invalid object type in empty: {redundant_filler['empty']} ")

            if 'cross_fade' in redundant_filler['empty']:
                cross_fade = redundant_filler['empty']['cross_fade']
                cross_fade = cross_fade if isinstance(cross_fade, numbers.Number) else DEFAULT_CROSS_FADE
                res_filler['empty'] = {
                    'cross_fade': cross_fade,
                }

            elif 'fade_in_out' in redundant_filler['empty']:
                fade_in = None
                fade_out = None
                fade_in_out_config = redundant_filler['empty']['fade_in_out']

                if fade_in_out_config is None:
                    fade_in_out_config = {}
                # logger.debug(f"type(fade_in_out_config):{type(fade_in_out_config)}")

                if not isinstance(fade_in_out_config, dict):
                    raise BadRequest(f"Invalid type of setting fade_in_out in {redundant_filler}")

                if 'fade_in' in fade_in_out_config:
                    fade_in = fade_in_out_config['fade_in']

                if 'fade_out' in fade_in_out_config:
                    fade_out = fade_in_out_config['fade_out']

                fade_in = fade_in if isinstance(fade_in, numbers.Number) else DEFAULT_FADE_IN
                fade_out = fade_out if isinstance(fade_out, numbers.Number) else DEFAULT_FADE_IN

                res_filler['empty'] = {
                    'fade_in_out': {
                        'fade_in': fade_in,
                        'fade_out': fade_out,
                    }
                }
            else:
                res_filler['empty'] = {
                    'cross_fade': DEFAULT_CROSS_FADE
                }

        elif 'bleep' in redundant_filler:
            res_filler['bleep'] = {}

    elif redundant_filler == 'empty':
        res_filler['empty'] = {
            'fade_in_out': {
                'fade_in': DEFAULT_FADE_IN,
                'fade_out': DEFAULT_FADE_OUT
            }
        }
    elif redundant_filler == 'bleep':
        res_filler['bleep'] = {}

    else:
        raise BadRequest("Unrecognised type of filler")

    return res_filler


def get_filler_type(redundant_filler: dict):
    res = ''
    if 'empty' in redundant_filler:
        res = 'empty'
    elif 'bleep' in redundant_filler:
        res = 'bleep'
    return res


def handle_redundants(redundants:dict):
    """
    :param redundants:
    redundants dict like:
    {
        'start': num,
        'end': num,
        'filler':
    }
    :return: redundants with filled params and corrected boundaries
    """
    redundants = sorted(redundants, key=lambda d: d['start'])
    filtered_redundants = []
    for redundant in redundants:
        logger.debug(f"redundant before: {redundant}")
        redundant['filler'] = fill_fade_settings(redundant['filler'])
        # logger.debug(f"redundant after: {redundant}")
        if len(filtered_redundants) == 0:
            filtered_redundants.append(redundant)
            continue

        logger.debug(filtered_redundants[-1])
        if filtered_redundants[-1]['end'] > redundant['start']:
            # logger.debug("came to first if")
            if all([
                filtered_redundants[-1]['end'] < redundant['end'],
                get_filler_type(filtered_redundants[-1]['filler']) != get_filler_type(redundant['filler'])
            ]):
                redundant['start'] = filtered_redundants[-1]['end']
                zero_fade_settings = {
                    'fade_in_out': {
                        'fade_in': 0,
                        'fade_out': 0,
                    }
                }
                if get_filler_type(filtered_redundants[-1]['filler']) == 'empty':
                    filtered_redundants[-1]['filler']['empty'] = zero_fade_settings
                else:
                    redundant['filler']['empty'] = zero_fade_settings
                # logger.debug("came to second if")
            else:
                filtered_redundants[-1]['end'] = max(redundant['end'], filtered_redundants[-1]['end'])
                # logger.debug(f"continue")
                continue

        filtered_redundants.append(redundant)

    logger.debug(f"filtered_redundants: {filtered_redundants}")
    return filtered_redundants


def cut_file(dir_path, file_name, redundants, file_name_beep):
    """
    recieve:
    dir_path - path to directory with file
    file_name - name of audio file in dir_path
    timestamps of redundants in seconds
    file_name_beep - path to bleeping file
    """

    # src_file = os.path.join(dir_path, file_name)
    audio = AudioSegment.from_file(file_name, format="mp3")
    bleep = AudioSegment.from_file(file_name_beep, format="mp3")
    bleep = bleep[1000:2000]
    logger.debug(f"Sorted redundants: {str(redundants)}")
    handle_redundants(redundants)

    for redundant in reversed(redundants):
        start_redundant = max(redundant['start'] * 1000 - 50, 0)
        end_redundant = redundant['end'] * 1000 + 50
        redundant_filler = redundant['filler']

        logger.debug(f"redundant_filler before processing: {redundant_filler}")
        redundant_filler = fill_fade_settings(redundant_filler)
        logger.debug(f"redundant_filler after processing: {redundant_filler}")

        filler_type = get_filler_type(redundant_filler)

        if filler_type == 'empty':
            if 'cross_fade' in redundant_filler['empty']:
                cross_fade = redundant_filler['empty']['cross_fade']

                rest_in_end = len(audio) - end_redundant
                cross_fade = min(cross_fade, start_redundant, rest_in_end)
                logger.debug(f"Resulted cross_fade: {cross_fade}")

                start_audio = audio[:start_redundant]
                end_audio = audio[end_redundant:]
                audio = start_audio.append(end_audio, crossfade=cross_fade)

            elif 'fade_in_out' in redundant_filler['empty']:
                start_audio = audio[:start_redundant].fade_out(fade_out)
                end_audio = audio[end_redundant:].fade_in(fade_in)
                audio = start_audio + end_audio
            else:
                raise BadRequest(f"Unrecorgnied redundant filler {redundant_filler}")

        elif filler_type == 'bleep':
            total_len = end_redundant - start_redundant
            cnt = total_len // 1000

            extended_bleep = bleep * int(cnt + 1)

            audio = audio[:start_redundant] + extended_bleep[:total_len] + audio[end_redundant:]

        else:
            raise BadRequest(f"Unrecorgnied redundant filler {redundant_filler}")

    out_file = os.path.join(dir_path, "clear.mp3")
    audio.export(out_file, format="mp3")

    return out_file
