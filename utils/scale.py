import operator


def detect_scale(notes: list[str]):
    pitches = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    distribution = dict((note, 0) for note in pitches)
    note_to_int = dict((note, number) for number, note in enumerate(pitches))
    int_to_note = dict((number, note) for number, note in enumerate(pitches))
    for el in notes:
        for n in el.split('.'):
            pitch = n[0:-1]
            distribution[pitch] += 1
    moods_shifts = {"Maj": [0, 2, 4, 5, 7, 9, 11],
                    "min": [0, 2, 3, 5, 7, 8, 10]}
    scales_prob = {}
    for pitch in pitches:
        for mood in moods_shifts.keys():
            in_tune_notes = 0
            for shift in moods_shifts[mood]:
                in_tune_notes += distribution[
                    int_to_note[(note_to_int[pitch] + shift) % 12]
                    ]
            scales_prob[pitch + mood] = in_tune_notes
    chosen_scale = max(scales_prob.items(), key=operator.itemgetter(1))[0]
    print(chosen_scale)
    scale_mood = chosen_scale[-3:]
    scale_tone = chosen_scale[0:-3]
    scale_notes = []  # in ints
    for shift in moods_shifts[scale_mood]:
        scale_notes.append((note_to_int[scale_tone] + shift) % 12)
    return chosen_scale, sorted(scale_notes)


def fix_note_by_scale(scale_notes, int_note):
    if int_note in scale_notes:
        return int_note
    else:
        return min(scale_notes, key=lambda x: abs(x - int_note))


def fix_scale(notes: list[str]) -> list[str]:
    """
    Returns a new list of notes that is corrected to fit the
    automatically detected scale.
    """
    scale, scale_notes = detect_scale(notes)
    pitches = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    note_to_int = dict((note, number) for number, note in enumerate(pitches))
    int_to_note = dict((number, note) for number, note in enumerate(pitches))
    corrected_notes = []
    for el in notes:
        better_el = []
        for note in el.split('.'):
            note_pitch = note[0:-1]
            note_octave = note[-1:]
            int_note = note_to_int[note_pitch]
            better_el.append(
                int_to_note[fix_note_by_scale(scale_notes, int_note)] +
                note_octave
                )
        corrected_notes.append('.'.join(better_el))
    return corrected_notes


if __name__ == "__main__":
    notes = ["F#3.A#3.C#4", "D4.F#4.A4", "E4.G#4.B4", "F#5"]
    print(fix_scale(notes))
