from .MinorMusicGenerator import MinorMusicGenerator
from music21 import stream, note, chord, tempo, meter, metadata, key
import random
import os
# from music21 import environment
#   type "which mscore" in console and insert your path here
# env = environment.Environment()
# env['musicxmlPath'] =  '/usr/local/bin/mscore'

tempo_map = {'Normal': 100, 'Slow': 60, 'Fast': 120}
number_to_scale = {59: 'B', 60: 'C', 61: 'C', 62: 'D', 63: 'Eb', 64: 'E',
                   65: 'F', 66: 'F', 67: 'G', 68: 'G', 69: 'A', 70: 'Bb'}


# it indicates the last chord for the left hand to make sequences unique
left_hand_last_chord_index = 0
right_hand_last_note_index = 0


def generate_music02(scale: int, name_of_the_file: int, pulse: str = 'Normal',
                     duration_sec: int = 60):
    INTERVAL_LENGTH = 3
    OCTAVE_SHIFT = 12
    # Initialize music generator
    new_song_generator = MinorMusicGenerator(scale)
    # + new_song_generator.additional_chords
    chords = new_song_generator.minor_chords

    right_hand_notes = new_song_generator.correct_notes.copy()

    # Add notes from the 5th octave
    for i in range(7):
        right_hand_notes.append(right_hand_notes[i] + OCTAVE_SHIFT)

    # List of possible notes for the right hand
    CORRECT_NOTES_COUNT = len(right_hand_notes)

    # Get BPM
    bpm = tempo_map.get(pulse, tempo_map['Normal'])

    # Initialize parts
    right_hand = stream.Part()
    left_hand = stream.Part()

    tonality = number_to_scale[scale]
    key_signature = key.Key(tonality + " m")  # "m" means minor

    right_hand.append(key_signature)
    right_hand.append(meter.TimeSignature('3/4'))
    right_hand.insert(0, tempo.MetronomeMark(number=bpm))
    left_hand.append(key_signature)
    left_hand.append(meter.TimeSignature('3/4'))
    left_hand.insert(0, tempo.MetronomeMark(number=bpm))

    # Calculate number of quarters
    quarters_count = duration_sec * (bpm / 60)
    durations = [3, 1.5, 1, 0.5]

    def add_one_interval():
        global right_hand_last_note_index
        # Choose a duration of each note for the current interval
        # (only for the right hand)
        random_duration_index = random.randint(0, len(durations) - 1)
        current_duration = durations[random_duration_index]

        velocity = random.randint(80, 110)
        # Generate notes for the right hand
        notes_count = int(INTERVAL_LENGTH / current_duration)
        for i in range(notes_count):
            if (random.randint(1, 11) % 7 == 0):  # drop notes randomly
                continue

            if (random.randint(1, 13) % 11 == 0):  # break the interval
                # Insert a pause of specified duration
                pause_duration = INTERVAL_LENGTH - i * current_duration
                pause_note = note.Rest()
                pause_note.duration.quarterLength = pause_duration
                right_hand.append(pause_note)
                break
            # add a chord instead of a single note
            if (random.randint(1, 5) % 3 == 0):
                random_index = random.randint(0, len(chords) - 1)
                random_chord = chords[random_index].copy()
                newChord = chord.Chord(
                    random_chord, quarterLength=current_duration)
                for my_note in newChord:
                    my_note.keySignature = key_signature
                newChord.volume.velocity = velocity
                right_hand.append(newChord)
                continue

            random_delta_index = random.randint(-1, 1)
            current_note_index = (
                right_hand_last_note_index + random_delta_index) % \
                CORRECT_NOTES_COUNT
            right_hand_last_note_index = current_note_index
            random_note = right_hand_notes[current_note_index]
            my_note = note.Note(random_note, quarterLength=current_duration)
            my_note.keySignature = key_signature
            my_note.volume.velocity = velocity
            right_hand.append(my_note)

        def add_chord_left_hand(idx: int, chord_shift: int, chord_velocity):
            random_chord = chords[idx].copy()
            random_chord.pop(random.randint(0, len(random_chord) - 1))
            for i in range(len(random_chord)):
                random_chord[i] -= OCTAVE_SHIFT * chord_shift
            newChord = chord.Chord(random_chord, quarterLength=1)
            for my_note in newChord:
                my_note.keySignature = key_signature
            newChord.volume.velocity = chord_velocity
            left_hand.append(newChord)

        global left_hand_last_chord_index

        # Choose a chord for the left hand
        random_index = random.randint(0, len(chords) - 1)
        while (random_index == left_hand_last_chord_index):
            random_index = random.randint(0, len(chords) - 1)
        left_hand_last_chord_index = random_index

        # Add a chord that contains two notes, which are the same but at
        # neighbouring octaves (for the left hand)
        random_chord = [chords[random_index][0] -
                        OCTAVE_SHIFT, chords[random_index][0]]
        newChord = chord.Chord(random_chord, quarterLength=1)
        for my_note in newChord:
            my_note.keySignature = key_signature
        newChord.volume.velocity = 128
        left_hand.append(newChord)
        # Add two more chords for the left hand
        add_chord_left_hand(random_index, 0, 85)
        add_chord_left_hand(random_index, 0, 115)

    # Generate music
    while right_hand.duration.quarterLength < quarters_count:
        add_one_interval()

    # Combine hands into stream
    myStream = stream.Stream([right_hand, left_hand])
    myStream.metadata = metadata.Metadata()
    myStream.metadata.title = "Waltz"
    myStream.metadata.composer = "RESO"
    # Write to MIDI and PDF file
    filepath_midi = os.path.join("generated_data", f"{name_of_the_file}.mid")
    filepath_pdf = os.path.join("generated_data", f"{name_of_the_file}.pdf")
    myStream.write('midi', fp=filepath_midi)
    myStream.write('musicxml.pdf', fp=filepath_pdf)

    # For this download MuseScore 3
    # myStream.show()
