from music21 import converter, note, chord, clef, tempo, meter, bar, metadata
from tqdm import tqdm
import os


def format_note(note) -> str:
    return str(note).replace('-', '')


def remove_leading_rests(lst):
    while lst and classify_element(lst[0]) in ['rest', 'useless']:
        lst.pop(0)
    return lst


def classify_element(e) -> str:
    if isinstance(e, note.Note):
        return "note"
    if isinstance(e, chord.Chord):
        return "chord"
    if isinstance(e, note.Rest):
        return "rest"
    if (isinstance(e, bar.Barline) or
            isinstance(e, clef.TrebleClef) or
            isinstance(e, meter.base.TimeSignature) or
            isinstance(e, tempo.MetronomeMark) or
            isinstance(e, clef.BassClef) or
            isinstance(e, metadata.Metadata)):
        return "useless"


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
        for e in remove_leading_rests(elements_to_parse):
            match classify_element(e):
                case "note":
                    notes.append(format_note(e.pitch))
                case "chord":
                    notes.append('.'.join(format_note(n) for n in e.pitches))
                case "rest":
                    notes.append("Rest")
                case "useless":
                    continue
                case _:
                    print(f"Unhandled type {type(e)}")
    return notes


if __name__ == "__main__":
    notes = get_notes_from_files("data/Mozart")
    print(notes[0:20])
