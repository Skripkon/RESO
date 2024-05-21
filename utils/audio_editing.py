import os

import audioread
from pydub import AudioSegment


def str_to_secs(time_str: str) -> int:
    """
    Converts string in format 'mm:ss' to seconds as an integer.
    """
    minutes, seconds = time_str.split(':')
    return int(minutes) * 60 + int(seconds)


def edit_mp3(relative_file_path: str,
             start_time: int,
             end_time: int,
             edit_id: int,
             fade_in_len=0,
             fade_out_len=0
             ) -> str:
    """
    Cuts an mp3 file according to given time and applies
    fade-in and fade-out.
    Receieves a path to original mp3, start and end times in seconds,
    fade-in and fade-out length in seconds.
    Resulting file is saved to the same folder
    with prefix 'edited_' and suffix '_{edits_count}' in mp3 format.
    If you do not need fade-in or fade-out, you do not have to
    specify fade_in_len or fade_out_len. Returns edited file name.
    """
    file_path = os.path.abspath(relative_file_path)

    # Read audio file using audioread
    with audioread.audio_open(file_path) as f:
        duration = f.duration

    # Convert start and end times to milliseconds
    start_ms = start_time * 1000
    end_ms = end_time * 1000

    # Ensure end time does not exceed duration
    end_ms = min(end_ms, duration * 1000)

    # Create AudioSegment object by loading the audio data
    full_audio = AudioSegment.empty()
    full_audio += AudioSegment.silent(duration=start_ms)  # Add silent audio before start time
    full_audio += AudioSegment.from_file(file_path)[start_ms:end_ms]  # Add audio data within the specified range

    # Apply fade-in/fade-out if needed
    if fade_in_len > 0:
        full_audio = full_audio.fade_in(fade_in_len * 1000)
    if fade_out_len > 0:
        full_audio = full_audio.fade_out(fade_out_len * 1000)

    export_path = os.path.join(os.path.dirname(
        file_path), "edited_" + os.path.basename(file_path).
            split('.')[0] + f'_{edit_id}.mp3')

    full_audio.export(export_path, format="mp3")
    return ("edited_" + os.path.basename(file_path).
            split('.')[0] + f'_{edit_id}.mp3')
