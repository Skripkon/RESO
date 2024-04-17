from pydub import AudioSegment
import os


def midi2mp3(filename: int):
    """
    Converts a specified .mid file into an .mp3 file
    and puts it into the same directory
    """
    try:
        filepath = os.path.join("generated_data", f"{filename}.mid")
        wav_file = os.path.join("generated_data", f"{filename}.wav")
        soundfont = os.path.abspath('utils/piano_soundfont.sf2')
        # Run the conversion from .mid to .wav
        os.system(
            f'fluidsynth -ni "{soundfont}" "{filepath}"\
            -F "{wav_file}" -r 44100')
        # Convert to .mp3 from .wav
        audio = AudioSegment.from_wav(wav_file)
        mp3_file = os.path.join("generated_data", f"{filename}.mp3")
        audio.export(mp3_file, format='mp3')
        os.remove(wav_file)

        return mp3_file

    except Exception as e:
        return f"Error conversion: {str(e)}"
