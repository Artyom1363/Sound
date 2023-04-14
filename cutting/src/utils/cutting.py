from pydub import AudioSegment
import os


def cut_file(dir_path, file_name, redundants):
    """
    recieve:
    path to directory with file
    path to audio file
    timestamps of redundants in seconds
    """

    src_file = os.path.join(dir_path, file_name)
    audio = AudioSegment.from_file(src_file, format="mp3")
    for redundant in reversed(redundants):
        start_redundant = redundant['start'] * 1000
        end_redundant = redundant['end'] * 1000
        audio = audio[:start_redundant] + audio[end_redundant:]


    out_file = os.path.join(dir_path, "clear.mp3")
    audio.export(out_file, format="mp3")
    # print("src_file: ", src_file, "\nout_file: ", out_file)
    return out_file
