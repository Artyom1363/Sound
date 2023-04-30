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
DEFAULT_ADDITION = 0
DEFAULT_EMPTY = {
    'cross_fade': DEFAULT_CROSS_FADE,
}

def fill_empty_setting(empty_filler):
    # logger.debug(f"{empty_filler=}")
    res_setting = {}
    if empty_filler is None:
        empty_filler = {}

    if not isinstance(empty_filler, dict):
        logger.info(f"Invalid object type in empty: {empty_filler}")
        raise BadRequest(f"Invalid object type in empty: {empty_filler}")

    if 'cross_fade' in empty_filler:
        cross_fade = empty_filler['cross_fade']
        if not any([
            cross_fade is None,
            isinstance(cross_fade, numbers.Number) and cross_fade >= 0
        ]):
            raise BadRequest(f"Invalid value in cross_fade: {cross_fade}")

        cross_fade = cross_fade if isinstance(cross_fade, numbers.Number) else DEFAULT_CROSS_FADE
        res_setting = {
            'cross_fade': cross_fade,
        }

    elif 'fade_in_out' in empty_filler:
        fade_in = None
        fade_out = None
        fade_in_out_config = empty_filler['fade_in_out']

        if fade_in_out_config is None:
            fade_in_out_config = {}

        if not isinstance(fade_in_out_config, dict):
            raise BadRequest(f"Invalid type of setting fade_in_out in {redundant_filler}")

        if 'fade_in' in fade_in_out_config:
            fade_in = fade_in_out_config['fade_in']
            # logger.debug(f"{fade_in=}")
            if not any([
                fade_in is None,
                isinstance(fade_in, numbers.Number) and fade_in >= 0
            ]):
                raise BadRequest(f"Invalid fade_in in {fade_in_out_config}")

        if 'fade_out' in fade_in_out_config:
            fade_out = fade_in_out_config['fade_out']

            if not any([
                fade_out is None,
                isinstance(fade_out, numbers.Number) and fade_out >= 0
            ]):
                raise BadRequest(f"Invalid fade_out in {fade_in_out_config}")


        fade_in = fade_in if isinstance(fade_in, numbers.Number) else DEFAULT_FADE_IN
        fade_out = fade_out if isinstance(fade_out, numbers.Number) else DEFAULT_FADE_IN

        res_setting = {
            'fade_in_out': {
                'fade_in': fade_in,
                'fade_out': fade_out,
            }
        }
    else:
        res_setting = DEFAULT_EMPTY

    return res_setting


def fill_fade_settings(redundant_filler: dict):
    res_filler = {}
    if type(redundant_filler) == dict:
        if 'empty' in redundant_filler:
            res_filler['empty'] = fill_empty_setting(redundant_filler['empty'])

        elif 'bleep' in redundant_filler:
            res_filler['bleep'] = {}

    elif redundant_filler == 'empty':
        res_filler['empty'] = DEFAULT_EMPTY
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


def correct_overlapped_boundaries(redundants:list):
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
    # import pdb
    # pdb.set_trace()
    redundants = sorted(redundants, key=lambda d: d['start'])
    filtered_redundants = []
    for redundant in redundants:
        # logger.debug(f"redundant before: {redundant}")

        if len(filtered_redundants) == 0:
            filtered_redundants.append(redundant)
            continue

        # logger.debug(filtered_redundants[-1])
        if filtered_redundants[-1]['end'] > redundant['start']:
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
            else:
                filtered_redundants[-1]['end'] = max(redundant['end'], filtered_redundants[-1]['end'])
                continue

        filtered_redundants.append(redundant)

    return filtered_redundants


def preprocess_redundants(redundants:list):
    if not isinstance(redundants, list):
        raise BadRequest("Redundants must be in list")

    processed_redundants = []
    for redundant in redundants:
        if not isinstance(redundant, dict):
            raise BadRequest("Every redundant must be described as dict")

        allowable_keys = ['start', 'end', 'filler']

        for key in allowable_keys:
            if key not in redundant:
                raise BadRequest(f'There is no {key} in {redundant}')

        for key in redundant:
            if key not in allowable_keys:
                raise BadRequest(f'Unrecornized key {key} in {redundant}')

        # import pdb
        # pdb.set_trace()
        # logger.debug(f"{redundant['start']=}  {isinstance(redundant['start'], numbers.Number)=}")
        if not all([
            isinstance(redundant['start'], numbers.Number),
            isinstance(redundant['end'], numbers.Number),
        ]):
            raise BadRequest('Boundaries must be numeric')

        if not all([
            redundant['start'] >= 0,
            redundant['end'] >= redundant['start']
        ]):
            raise BadRequest("Boundaries must be: 0 <= left <= right")

        processed_redundant = redundant
        processed_redundant['filler'] = fill_fade_settings(redundant['filler'])
        processed_redundants.append(processed_redundant)

    return correct_overlapped_boundaries(processed_redundants)


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
    logger.info(f"Source redundants: {redundants}")
    redundants = preprocess_redundants(redundants)
    logger.debug(f"Handled redundants: {redundants}")

    for redundant in reversed(redundants):
        start_redundant = max(redundant['start'] * 1000 - DEFAULT_ADDITION, 0)
        end_redundant = min(redundant['end'] * 1000 + DEFAULT_ADDITION, len(audio))
        redundant_filler = redundant['filler']

        logger.debug(f"redundant_filler before processing: {redundant_filler}")
        redundant_filler = fill_fade_settings(redundant_filler)
        logger.debug(f"redundant_filler after processing: {redundant_filler}")

        filler_type = get_filler_type(redundant_filler)

        if filler_type == 'empty':
            if 'cross_fade' in redundant_filler['empty']:
                cross_fade = redundant_filler['empty']['cross_fade']

                rest_in_end = len(audio) - end_redundant
                logger.debug(f'{cross_fade=}, {start_redundant=}, {rest_in_end=}')
                cross_fade = min(cross_fade, start_redundant, rest_in_end)
                cross_fade = max(cross_fade, 0)
                logger.debug(f"Resulted cross_fade: {cross_fade}")

                start_audio = audio[:start_redundant]
                end_audio = audio[end_redundant:]
                audio = start_audio.append(end_audio, crossfade=cross_fade)

            elif 'fade_in_out' in redundant_filler['empty']:
                fade_out = redundant_filler['empty']['fade_in_out']['fade_out']
                fade_in = redundant_filler['empty']['fade_in_out']['fade_in']

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
