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
    # stupid_audio = AudioSegment.from_file(src_file, format="mp3")
    for redundant in reversed(redundants):
        start_redundant = redundant['start'] * 1000 - 200
        end_redundant = redundant['end'] * 1000 + 100
        start_audio = audio[:start_redundant].fade_out(150)
        end_audio = audio[end_redundant:].fade_in(150)
        audio = start_audio + end_audio
        # stupid_audio = stupid_audio[:start_redundant] + stupid_audio[end_redundant:]


    out_file = os.path.join(dir_path, "clear.mp3")
    # out_file_stupid = os.path.join(dir_path, "stupid.mp3")
    # out_file_smooth = os.path.join(dir_path, "smooth.mp3")
    audio.export(out_file, format="mp3")
    # stupid_audio.export(out_file_stupid, format="mp3")
    # audio.export(out_file, format="mp3")
    # print("src_file: ", src_file, "\nout_file: ", out_file)
    return out_file


def format_file(dir_path, file_name):
    """
    recieve:
    path to directory with file
    path to audio file
    """
    pass
    # src_file = os.path.join(dir_path, file_name)
    # src_file = "data/beeping.mp3"
    # audio = AudioSegment.from_file(src_file, format="mp3")
    # # for redundant in reversed(redundants):
    # #     start_redundant = redundant['start'] * 1000
    # #     end_redundant = redundant['end'] * 1000
    #     # start_redundant += 5
    # # first_5_sec = audio[0:5000]
    # # first_5_sec += 20
    # # second_5_sec = audio[5000:10000]
    # # cros = first_5_sec.append(second_5_sec, crossfade=3000)
    # # # audio[0:5000] += 10
    # # new_audio = first_5_sec + audio[5000:]
    # # fade_in = first_5_sec.fade_in(2000)
    # # fade_out = first_5_sec.fade_out(2000)
    #
    #     # audio = audio[:start_redundant] + audio[end_redundant:]
    #
    # out_file = os.path.join(dir_path, "formatted1.mp3")
    # out_file2 = os.path.join(dir_path, "formatted2.mp3")
    # fade_in_file = os.path.join(dir_path, "fade_in.mp3")
    # fade_out_file = os.path.join(dir_path, "fade_out.mp3")
    # audio.export(out_file, format="mp3")
    # # audio[0:5000] = first_5_sec
    # cros.export(out_file2, format="mp3")
    # fade_in.export(fade_in_file, format="mp3")
    # fade_out.export(fade_out_file, format="mp3")
    # # print("src_file: ", src_file, "\nout_file: ", out_file)
    # # return out_file

