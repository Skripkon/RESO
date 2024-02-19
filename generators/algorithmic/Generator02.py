from .MinorMusicGenerator import MinorMusicGenerator
from music21 import stream, note, chord, tempo, meter
import random

tempo_map = {'Normal': 100, 'Slow': 60, 'Fast': 120}
velocity = 100

def generate_music02(scale: int, filepath: str, pulse: str = 'Normal', duration_sec: int = 60):
    # Initialize music generator
    new_song_generator = MinorMusicGenerator(scale)
    new_song_generator.minor_chords += new_song_generator.additional_chords

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

    def add_one_interval(octave_shift_from_4: int = 0):
        shift = octave_shift_from_4 * 12

        # Generate notes for right hand
        rest = note.Rest()
        rest.duration.quarterLength = 0.5
        right_hand.append(rest)
        for _ in range(5):
            random_note = random.choice(new_song_generator.correct_notes) + shift
            my_note = note.Note(random_note, quarterLength=0.5)
            my_note.volume.velocity = velocity / 3
            right_hand.append(my_note)

        # random_note1 = random.choice(new_song_generator.correct_notes) + shift
        # random_note2 = random.choice(new_song_generator.correct_notes) + shift
        # my_note1 = note.Note(random_note1, quarterLength=1)
        # my_note2 = note.Note(random_note2, quarterLength=2)
        # my_note1.volume.velocity = velocity / 2
        # my_note2.volume.velocity = velocity / 2
        # right_hand.append(my_note1)
        # right_hand.append(my_note2)

        # Generate chords for left hand
        random_chord = random.choice(new_song_generator.minor_chords)[:-1]
        newChord = chord.Chord(random_chord, quarterLength=1)
        newChord.volume.velocity = velocity / 1.5
        left_hand.append(newChord)

        for _ in range(2):
            random_chord = random.choice(new_song_generator.minor_chords)[:-1]
            newChord = chord.Chord(random_chord, quarterLength=1)
            newChord.volume.velocity = velocity / 3
            left_hand.append(newChord)

    # Generate music
    while right_hand.duration.quarterLength < number_of_quarters:
        add_one_interval(octave_shift_from_4=random.randint(-1, 1))

    # Combine hands into stream
    myStream = stream.Stream([right_hand, left_hand])

    # Write to MIDI file
    myStream.write('midi', fp=filepath)

    # For this download MuseScore 3
    # myStream.show()

# generate_waltz_music(59, "waltz_music.midi", pulse='Normal', duration_sec=60)
