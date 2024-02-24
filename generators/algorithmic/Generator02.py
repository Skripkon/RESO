from MinorMusicGenerator import MinorMusicGenerator
from music21 import stream, note, chord, tempo, meter
import random

tempo_map = {'Normal': 100, 'Slow': 60, 'Fast': 120}

# it indicates the last chord for the left hand, so we can make sequences unique
last_chord_for_the_left_hand_index = 0
index_of_the_last_note_for_the_right_hand = 0


def generate_music02(scale: int, filepath: str, pulse: str = 'Normal', duration_sec: int = 60):
    LENGTH_OF_THE_INTERVAl = 3
    # Initialize music generator
    new_song_generator = MinorMusicGenerator(scale)
    # + new_song_generator.additional_chords
    chords = new_song_generator.minor_chords

    notes_for_the_right_hand = new_song_generator.correct_notes.copy()

    for i in range(7):  # add notes from the 5th octave
        notes_for_the_right_hand.append(notes_for_the_right_hand[i] + 12)

    # list of possible notes for the right hand
    NUMBER_OF_NOTEX = len(notes_for_the_right_hand)

    # Get BPM
    bpm = tempo_map.get(pulse, tempo_map['Normal'])

    # Initialize parts
    right_hand = stream.Part()
    left_hand = stream.Part()
    right_hand.append(meter.TimeSignature('3/4'))
    right_hand.insert(0, tempo.MetronomeMark(number=bpm))
    left_hand.append(meter.TimeSignature('3/4'))
    left_hand.insert(0, tempo.MetronomeMark(number=bpm))

    # Calculate number of quarters
    number_of_quarters = duration_sec * (bpm / 60)
    durations = [3, 1.5, 1, 0.5]

    def add_one_interval():
        global index_of_the_last_note_for_the_right_hand
        # choose a duration of each note for the current interval (only for the right hand)
        random_duration_index = random.randint(0, len(durations) - 1)
        current_duration = durations[random_duration_index]

        velocity = random.randint(80, 110)
        # Generate notes for the right hand
        number_of_notes = int(LENGTH_OF_THE_INTERVAl / current_duration)
        for i in range(number_of_notes):
            if (random.randint(1, 11) % 7 == 0):  # drop notes in a haphazard way
                continue

            if (random.randint(1, 13) % 11 == 0):  # break the interval
                # Insert a pause of specified duration
                pause_duration = LENGTH_OF_THE_INTERVAl - i * current_duration
                pause_note = note.Rest()
                pause_note.duration.quarterLength = pause_duration
                right_hand.append(pause_note)
                break

            if (random.randint(1, 5) % 3 == 0):  # add a chord instead of a single note
                random_index = random.randint(0, len(chords) - 1)
                random_chord = chords[random_index].copy()
                newChord = chord.Chord(
                    random_chord, quarterLength=current_duration)
                newChord.volume.velocity = velocity
                right_hand.append(newChord)
                continue

            random_delta_index = random.randint(-1, 1)
            index_of_the_current_note = (index_of_the_last_note_for_the_right_hand +
                                         random_delta_index) % NUMBER_OF_NOTEX
            index_of_the_last_note_for_the_right_hand = index_of_the_current_note
            random_note = notes_for_the_right_hand[index_of_the_current_note]
            my_note = note.Note(random_note, quarterLength=current_duration)
            my_note.volume.velocity = velocity
            right_hand.append(my_note)

        def add_a_chord_to_the_left_hand(idx: int, chord_shift: int, chord_velocity):
            random_chord = chords[idx].copy()
            random_chord.pop(random.randint(0, len(random_chord) - 1))
            for i in range(len(random_chord)):
                random_chord[i] -= 12 * chord_shift
            newChord = chord.Chord(random_chord, quarterLength=1)
            newChord.volume.velocity = chord_velocity
            left_hand.append(newChord)

        global last_chord_for_the_left_hand_index

        # Choose a chord for the left hand
        random_index = random.randint(0, len(chords) - 1)
        while (random_index == last_chord_for_the_left_hand_index):
            random_index = random.randint(0, len(chords) - 1)
        last_chord_for_the_left_hand_index = random_index

        # Add a chord that contains two notes, which are the same but at
        # neighbouring octaves (for the left hand)
        random_chord = [chords[random_index][0] - 12, chords[random_index][0]]
        newChord = chord.Chord(random_chord, quarterLength=1)
        newChord.volume.velocity = 128
        left_hand.append(newChord)
        # Add two more chords for the left hand
        add_a_chord_to_the_left_hand(random_index, 0, 85)
        add_a_chord_to_the_left_hand(random_index, 0, 115)

    # Generate music
    while right_hand.duration.quarterLength < number_of_quarters:
        add_one_interval()

    # Combine hands into stream
    myStream = stream.Stream([right_hand, left_hand])
    # Write to MIDI file
    myStream.write('midi', fp=filepath)

    # For this download MuseScore 3
    # myStream.show()
