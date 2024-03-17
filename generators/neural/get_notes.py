from music21 import converter, note, chord, clef, tempo, meter, bar, metadata
from tqdm import tqdm
import os


def format_note(note) -> str:
    form_note = str(note).replace('-', '')
    format_note_octave = int(form_note[-1])
    format_note_pitch = form_note[0:-1]
    if format_note_octave < 3:
        return format_note_pitch + '3'
    if format_note_octave > 5:
        return format_note_pitch + '5'
    return form_note


def remove_leading_rests(lst):
    while lst and classify_element(lst[0]) in ['rest', 'useless']:
        lst.pop(0)
    return lst


def classify_element(e) -> str:
    if isinstance(e, note.Note):
        return "note"
    if isinstance(e, chord.Chord):
        return "chord"
    # if isinstance(e, note.Rest):
    #     return "rest"
    if (isinstance(e, bar.Barline) or
            isinstance(e, clef.TrebleClef) or
            isinstance(e, meter.base.TimeSignature) or
            isinstance(e, tempo.MetronomeMark) or
            isinstance(e, clef.BassClef) or
            isinstance(e, metadata.Metadata) or
            isinstance(e, note.Rest)):
        return "useless"


def format_chord(chord):
    new_chord = set()
    chord_pitches = set()
    for n in sorted(chord.pitches):
        n = format_note(n)
        note_octave = int(n[-1])
        note_pitch = n[0:-1]
        if note_pitch in chord_pitches:
            continue
        if note_octave < 3:
            new_chord.add(note_pitch + '3')
        elif note_octave > 4:
            new_chord.add(note_pitch + '4')
        else:
            new_chord.add(note_pitch + str(note_octave))
        chord_pitches.add(note_pitch)

    result = sorted(list(new_chord))

    if len(result) > 1:
        return '.'.join([str(n) for n in result])
    elif len(result) == 1:
        if int(result[0][-1]) <= 3:
            return result[0][0:-1] + '4'
        else:
            return result[0]

    raise Exception("EMPTY CHORD")


def get_notes_from_files(path: str) -> list:
    """
    Gets the sequence of all notes and chords from the MIDI files in the
    specified directory. Parses chords by joining their notes with '.',
    i.e. E G B -> E.G.B and rest notes are parsed as 'Rest'.
    """
    files = [os.path.join(path, file)
             for file in os.listdir(path) if file.endswith('.mid')]
    print(f"Parsing {len(files)} files from folder '{os.path.abspath(path)}'")
    notes = []
    for file in tqdm(files):
        midi = converter.parse(file)
        elements_to_parse = midi.flatten()
        for e in remove_leading_rests(elements_to_parse):
            match classify_element(e):
                case "note":
                    notes.append(format_note(e.pitch))
                case "chord":
                    form_chord = format_chord(e)
                    form_chord_len = len(form_chord.split('.'))
                    if form_chord_len >= 5:
                        continue
                    notes.append(form_chord)
                case "rest":
                    notes.append("Rest")
                case "useless":
                    continue
                case _:
                    print(f"Unhandled type {type(e)}")
    return notes


if __name__ == "__main__":
    notes = get_notes_from_files("data/Mozart")

    SEQUENCE_LENGTH = 200

    unique_notes = sorted(set(notes))
    note_to_int = dict((note, number) for number, note in
                       enumerate(unique_notes))
    int_to_note = dict((number, note) for number, note in
                       enumerate(unique_notes))

    input_sequences = []
    output_sequences = []

    for i in range(len(notes) - SEQUENCE_LENGTH):
        sequence_in = notes[i:i + SEQUENCE_LENGTH]
        sequence_out = notes[i + SEQUENCE_LENGTH]
        input_sequences.append([note_to_int[char] for char in sequence_in])
        output_sequences.append(note_to_int[sequence_out])

    print(len(unique_notes), len(input_sequences))
