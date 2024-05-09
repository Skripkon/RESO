import os

from pydub import AudioSegment


def midi2mp3(filename: int):
    """
    Converts a specified .mid file into an .mp3 file
    and puts it into the same directory
    """
    mp3_file = os.path.join("generated_data", f"{filename}.mp3")
    filepath = os.path.join("generated_data", f"{filename}.mid")
    wav_file = os.path.join("generated_data", f"{filename}.wav")
    soundfont = os.path.abspath('utils/piano_soundfont.sf2')
    try:
        # Run the conversion from .mid to .wav
        os.system(
            f'fluidsynth -ni "{soundfont}" "{filepath}"\
            -F "{wav_file}" -r 44100')
        # Convert to .mp3 from .wav
        audio = AudioSegment.from_wav(wav_file)
        audio.export(mp3_file, format='mp3')
        os.remove(wav_file)

    except Exception:  # this exception is for Linux systems only,
        # because sometimes fluidsynth doesn't work there
        os.system(
            # amplify volume by 200 percent and run a conversion
            f'timidity {filepath} -Ow -o {mp3_file} --volume=200'
        )
        try:
            os.remove(wav_file)
        except OSError:
            pass
    return mp3_file
