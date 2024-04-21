from .MinorMusicGenerator import MinorMusicGenerator
from music21 import stream, note, chord, tempo, metadata, key
import random
import os

tempo_map = {'Normal': 100, 'Slow': 60, 'Fast': 120}
number_to_scale = {59: 'B', 60: 'C', 61: 'C', 62: 'D', 63: 'Eb', 64: 'E',
                   65: 'F', 66: 'F', 67: 'G', 68: 'G', 69: 'A', 70: 'Bb'}


def generate_music01(scale: int, name_of_the_file: int,
                     pulse: str = 'Normal',
                     duration_sec: int = 60):
    new_song_generator = MinorMusicGenerator(scale)
    new_song_generator.minor_chords += new_song_generator.additional_chords
    number_of_possible_chords = len(new_song_generator.minor_chords)
    note_duration = [2, 1, 0.5]
    number_of_possible_durations = len(note_duration)
    right_hand = stream.Part()
    left_hand = stream.Part()

    bpm = tempo_map.get(pulse, tempo_map['Normal'])

    tonality = number_to_scale[scale]
    key_signature = key.Key(tonality + " m")  # "m" means minor
    right_hand.append(key_signature)
    left_hand.append(key_signature)
    right_hand.insert(0, tempo.MetronomeMark(number=bpm))
    left_hand.insert(0, tempo.MetronomeMark(number=bpm))

    quarters_count = int(duration_sec * (bpm / 60))
    intervals = quarters_count // 4

    def add_one_interval(octave_shift_from_4: int = 0,
                         velocity: int = 90):
        # generating notes for the right hand
        random_number = random.randint(0, number_of_possible_durations - 1)
        number_of_notes = 2 ** random_number
        duration = note_duration[random_number]
        shift: int = octave_shift_from_4 * 12
        for note_i in range(number_of_notes):
            random_note = new_song_generator.correct_notes[
                random.randint(
                    0, 6)] + shift
            my_note = note.Note(random_note, quarterLength=duration + 1)
            my_note.volume.velocity = velocity
            right_hand.append(my_note)

        # generating the chord for the left hand
        while left_hand.quarterLength < right_hand.quarterLength:
            random_chord = new_song_generator.minor_chords[
                random.randint(0, number_of_possible_chords - 1)]
            newChord = chord.Chord(random_chord, quarterLength=2)
            newChord.volume.velocity = 60
            left_hand.append(newChord)

    for i in range(intervals):
        add_one_interval(octave_shift_from_4=random.randint(-1, 1),
                         velocity=random.randint(70, 70))
    add_one_interval(velocity=50)

    # Combine hands into stream
    myStream = stream.Stream([right_hand, left_hand])
    myStream.metadata = metadata.Metadata()
    myStream.metadata.title = "Calm Melody"
    myStream.metadata.composer = "RESO"
    # Write to MIDI and PDF file
    filepath_midi = os.path.join("generated_data", f"{name_of_the_file}.mid")
    filepath_pdf = os.path.join("generated_data", f"{name_of_the_file}.pdf")
    myStream.write('midi', fp=filepath_midi)
    myStream.write('musicxml.pdf', fp=filepath_pdf)
