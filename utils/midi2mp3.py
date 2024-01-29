from pydub import AudioSegment
from music21 import converter
import os


def midi2mp3(file_name):
    try:
        wav_file = os.path.abspath(file_name.replace('.mid', '.wav'))
        mp3_file = os.path.abspath(file_name.replace('.mid', '.mp3'))
        # print("saving wav", wav_file)

        os.system(f'fluidsynth -ni piano_soundfont.sf2 {file_name} -F {wav_file} -r 44100')
    
        audio = AudioSegment.from_wav(wav_file)
        audio.export(mp3_file, format='mp3')

        os.remove(wav_file)
        # print("success", wav_file, mp3_file)
        return mp3_file

    except Exception as e:
        return f"Error conversion: {str(e)}"
