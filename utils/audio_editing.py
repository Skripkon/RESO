from pydub import AudioSegment
import os


def str_to_secs(time_str):
    minutes, seconds = time_str.split(':')
    return int(minutes) * 60 + int(seconds)


def edit_mp3(relative_file_path: str,
             start_time: int,
             end_time: int,
             edit_id: int,
             fade_in_len=0,
             fade_out_len=0
             ):
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
    full_audio = AudioSegment.from_mp3(file_path)

    # Cut to specified length
    cut_audio = full_audio[(start_time * 1000):(end_time * 1000)]

    # Apply fade-in/fade-out if needed
    if fade_in_len > 0:
        cut_audio = cut_audio.fade_in(fade_in_len * 1000)
    if fade_out_len > 0:
        cut_audio = cut_audio.fade_out(fade_out_len * 1000)

    export_path = os.path.join(os.path.dirname(
        file_path), "edited_" + os.path.basename(file_path).
            split('.')[0] + f'_{edit_id}.mp3')
    cut_audio.export(export_path, format="mp3")
    return ("edited_" + os.path.basename(file_path).
            split('.')[0] + f'_{edit_id}.mp3')


if __name__ == "__main__":
    # Assumes file is run from root repository folder
    edit_mp3("generated_data/gen_7.mp3", start_time=5,
             end_time=15, fade_in_len=1, fade_out_len=3)
