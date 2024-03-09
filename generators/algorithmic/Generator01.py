from .MinorMusicGenerator import MinorMusicGenerator
from music21 import note, chord, stream, metadata
import random
import os


def generate_music01(scale: int, name_of_the_file: int):
    new_song_generator = MinorMusicGenerator(scale)
    new_song_generator.minor_chords += new_song_generator.additional_chords
    number_of_possible_chords = len(new_song_generator.minor_chords)
    note_duration = [2, 1, 0.5]
    number_of_possible_durations = len(note_duration)
    intervals = 40
    right_hand = stream.Part()
    left_hand = stream.Part()

    def add_one_interval(index: int, octave_shift_from_4: int = 0,
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

        random_chord = new_song_generator.minor_chords[
            random.randint(0, number_of_possible_chords - 1)]
        newChord = chord.Chord(random_chord)
        newChord.volume.velocity = 60
        left_hand.insert(index, newChord)

    for i in range(intervals):
        add_one_interval(2 * i, octave_shift_from_4=random.randint(-1, 1),
                         velocity=random.randint(70, 70))
    add_one_interval(2 * intervals, velocity=50)

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
