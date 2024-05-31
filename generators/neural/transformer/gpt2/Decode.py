import note_seq

NOTE_LENGTH = 0.25 * 60 / 120
BAR_LENGTH = 4.0 * 60 / 120


def empty_note_sequence(qpm=120.0, total_time=0.0):
    note_sequence = note_seq.protobuf.music_pb2.NoteSequence()
    note_sequence.tempos.add().qpm = qpm
    note_sequence.ticks_per_quarter = note_seq.constants.STANDARD_PPQ
    note_sequence.total_time = total_time
    return note_sequence


def token_sequence_to_note_sequence(token_sequence, qpm, NOTE_LENGTH, BAR_LENGTH):

    if isinstance(token_sequence, str):
        token_sequence = token_sequence.split()

    note_sequence = empty_note_sequence(qpm=qpm)

    track_count = 0
    current_time = 0
    current_notes = {}
    for token_index, token in enumerate(token_sequence):
        if token == "PIECE_START":
            pass
        elif token == "PIECE_END":
            print("end")
            break
        elif token == "TRACK_START":
            current_bar_index = 0
            track_count += 1
            pass
        elif token == "BAR_START":
            current_time = current_bar_index * BAR_LENGTH
            current_notes = {}
        elif token == "BAR_END":
            current_bar_index += 1
            pass
        elif token.startswith("NOTE_ON"):
            pitch = int(token.split("=")[-1])
            note = note_sequence.notes.add()
            note.start_time = current_time
            note.end_time = current_time + 4 * NOTE_LENGTH
            note.pitch = pitch
            note.instrument = 0
            note.program = 0
            note.velocity = 80
            current_notes[pitch] = note
        elif token.startswith("NOTE_OFF"):
            pitch = int(token.split("=")[-1])
            if pitch in current_notes:
                note = current_notes[pitch]
                note.end_time = current_time
        elif token.startswith("TIME_DELTA"):
            delta = float(token.split("=")[-1]) * NOTE_LENGTH
            current_time += delta
        else:
            pass

    return note_sequence
