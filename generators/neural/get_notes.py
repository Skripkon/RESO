from music21 import converter, note, chord, clef, tempo, meter, bar, metadata
from tqdm import tqdm
import os


def format_note(note) -> str:
    return str(note).replace('-', '')


def get_notes_from_files(path: str) -> list:
    """
    Gets the sequence of all notes and chords from the MIDI files in the
    specified directory. Parses chords by joining their notes with '.',
    i.e. E G B -> E.G.B and rest notes are parsed as 'Rest'.
    """
    files = [os.path.join(path, file)
             for file in os.listdir(path) if file.endswith('.mid')]
    print(f"Parsing {len(files)} files from folder {path}")
    notes = []
    for file in tqdm(files):
        midi = converter.parse(file)
        elements_to_parse = midi.flatten()
        for e in elements_to_parse:
            match type(e):
                case note.Note:
                    notes.append(format_note(e.pitch))
                case chord.Chord:
                    notes.append('.'.join(format_note(n) for n in e.pitches))
                case note.Rest:
                    notes.append("Rest")
                case bar.Barline | clef.TrebleClef | meter.base.TimeSignature:
                    continue
                case tempo.MetronomeMark | clef.BassClef | metadata.Metadata:
                    continue
                case _:
                    print(f"Unhandled type {type(e)}")
    return notes


if __name__ == "__main__":
    get_notes_from_files("data/Mozart")
