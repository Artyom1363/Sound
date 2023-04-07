import subprocess
import soundfile

SAMPLE_RATE = 16000


def ffmpeg_convert(input_audiofile, output_audiofile, sr=SAMPLE_RATE):
    """
    Convert an audio file to a resampled audio file with the desired
    sampling rate specified by `sr`.
    Parameters
    ----------
    input_audiofile : string
            Path to the video or audio file to be resampled.
    output_audiofile
            Path for saving the resampled audio file. Should have .wav extension.
    sr : int
            The sampling rate to use for resampling (e.g. 16000, 44100, 48000).
    Returns
    -------
    completed_process : subprocess.CompletedProcess
            A process completion object. If completed_process.returncode is 0 it
            means the process completed successfully. 1 means it failed.
    """

    # fmpeg command
    cmd = ["ffmpeg", "-i", input_audiofile, "-ac", "1", "-af", "aresample=resampler=soxr", "-ar", str(sr), "-y", output_audiofile]
    # print(' '.join(cmd))
    # return
    completed_process = subprocess.run(cmd)

    # confirm process completed successfully
    assert completed_process.returncode == 0

    # confirm new file has desired sample rate
    assert soundfile.info(output_audiofile).samplerate == sr


def cut_file(src_filepath, tar_filepath, start_time, end_time):
    cut_cmd = ["ffmpeg", "-i", src_filepath, "-ss", str(start_time), "-to", str(end_time), tar_filepath]
    print(' '.join(cut_cmd))
    completed_process = subprocess.run(cut_cmd)
    assert completed_process.returncode == 0
