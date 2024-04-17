from pydub import AudioSegment
import subprocess
from pathlib import Path

SOUNDFONT_PATH = 'utils/piano_soundfont.sf2'
GENERATED_DATA_PATH = 'generated_data'


def midi2mp3(filename: int):
    """
    Converts a specified .mid file into an .mp3 file
    and puts it into the same directory
    """
    try:
        midi_file = Path(GENERATED_DATA_PATH) / f"{filename}.mid"
        wav_file = Path(GENERATED_DATA_PATH) / f"{filename}.wav"
        mp3_file = Path(GENERATED_DATA_PATH) / f"{filename}.mp3"

        # Convert .mid to .wav
        subprocess.run([
            'fluidsynth', '-ni', SOUNDFONT_PATH, str(midi_file),
            '-F', str(wav_file), '-r', '44100'
        ], check=True)

        # Convert .wav to .mp3
        audio = AudioSegment.from_wav(str(wav_file))
        audio.export(str(mp3_file), format='mp3')

        # Clean up temporary wav file
        wav_file.unlink()

        return mp3_file

    except subprocess.CalledProcessError as e:
        return f"Error conversion: {e}"
    except FileNotFoundError as e:
        return f"File not found: {e}"
    except Exception as e:
        return f"Unknown error: {e}"
