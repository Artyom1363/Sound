from pydub import AudioSegment
import logging
import os
from src import app_logger
from src.exceptions import BadRequest


logger = app_logger.get_logger(__name__)
DEFAULT_FADE_IN = 150
DEFAULT_FADE_OUT = 150
DEFAULT_CROSS_FADE = 200


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
    redundants = sorted(redundants, key=lambda d: d['start'])
    logger.debug(f"Sorted redundants: {str(redundants)}")

    for redundant in reversed(redundants):
        start_redundant = max(redundant['start'] * 1000 - 50, 0)
        end_redundant = redundant['end'] * 1000 + 50
        redundant_filler = redundant['filler']

        if redundant_filler == 'bleep':

            total_len = end_redundant - start_redundant
            cnt = total_len // 1000

            extended_bleep = bleep * int(cnt + 1)

            audio = audio[:start_redundant] + extended_bleep[:total_len] + audio[end_redundant:]

        elif redundant_filler == 'empty':

            start_audio = audio[:start_redundant].fade_out(150)
            end_audio = audio[end_redundant:].fade_in(150)
            audio = start_audio + end_audio

        elif type(redundant_filler) == dict:
            if 'empty' in redundant_filler:
                if type(redundant_filler['empty']) != dict:
                    logger.debug("Got file without type of formatting")
                elif 'cross_fade' in redundant_filler['empty']:
                    cross_fade = redundant_filler['empty']['cross_fade']
                    cross_fade = DEFAULT_CROSS_FADE if cross_fade is None else cross_fade

                    rest_in_end = len(audio) - end_redundant
                    cross_fade = min(cross_fade, start_redundant, rest_in_end)
                    logger.debug(f"Resulted cross_fade: {cross_fade}")

                    start_audio = audio[:start_redundant]
                    end_audio = audio[end_redundant:]
                    audio = start_audio.append(end_audio, crossfade=cross_fade)

                elif 'fade_in_out' in redundant_filler['empty']:
                    fade_in = None
                    fade_out = None
                    fade_in_out_config = redundant_filler['empty']['fade_in_out']

                    if (fade_in_out_config is not None) and ('fade_in' in fade_in_out_config):
                        fade_in = fade_in_out_config['fade_in']

                    if (fade_in_out_config is not None) and ('fade_out' in fade_in_out_config):
                        fade_out = fade_in_out_config['fade_out']

                    fade_in = DEFAULT_FADE_IN if fade_in is None else fade_in
                    fade_out = DEFAULT_FADE_OUT if fade_out is None else fade_out
                    logger.debug(f"Resulted fade_in: {fade_in} fade_out: {fade_out}")
                    start_audio = audio[:start_redundant].fade_out(fade_out)
                    end_audio = audio[end_redundant:].fade_in(fade_in)
                    audio = start_audio + end_audio

            elif 'bleep' in redundant_filler:
                total_len = end_redundant - start_redundant
                cnt = total_len // 1000

                extended_bleep = bleep * int(cnt + 1)

                audio = audio[:start_redundant] + extended_bleep[:total_len] + audio[end_redundant:]

        else:
            # print("ERROR: unsupported format")
            logger.error('ERROR: unsupported format')

    out_file = os.path.join(dir_path, "clear.mp3")
    audio.export(out_file, format="mp3")

    return out_file
