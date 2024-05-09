from .MinorMusicGenerator import MinorMusicGenerator
from music21 import stream, note, chord, tempo, meter, metadata
import os
import random

tempo_map = {'Normal': 100, 'Slow': 60, 'Fast': 120}


def generate_music03(scale: int, filename: int, pulse: str = 'Normal',
                     duration_sec: int = 60):
    
    INTERVAL_LENGTH = 3 # 20 notes in a left hand. Duration of each note is 0.25
    OCTAVE_SHIFT: int = 12

    new_song_generator = MinorMusicGenerator(scale)
    myStream = stream.Stream()

    right_hand_chords = new_song_generator.minor_chords.copy()
    right_hand_notes = new_song_generator.correct_notes.copy()

    # List of possible notes for the right hand
    CORRECT_NOTES_COUNT = len(right_hand_notes)

    # Get BPM
    bpm = tempo_map.get(pulse, tempo_map['Normal'])
    volumes = [120, 50, 60, 80, 90, 110, 120, 110, 90, 80, 70, 50]
    
    # Initialize parts
    right_hand = stream.Part()
    left_hand = stream.Part()
    right_hand.append(meter.TimeSignature('3/4'))
    right_hand.insert(0, tempo.MetronomeMark(number=bpm))
    left_hand.append(meter.TimeSignature('3/4'))
    left_hand.insert(0, tempo.MetronomeMark(number=bpm))

    # Calculate number of quarters
    quarters_count = duration_sec * (bpm / 60)

    number_of_notes = [1, 2, 3, 6, 12] # this list is needed to randomize a number of notes for a single interval;
    # a duration of each note is then determined by the following formula: INTERVAL_LENGTH / number_of_notes

    def add_one_interval():

        # Choose the number of notes for the right hand
        notes_count = number_of_notes[random.randint(0, len(number_of_notes) - 1)]
        current_duration = INTERVAL_LENGTH / notes_count
        velocity = random.randint(80, 100)

        # Generate notes for the right hand
        for i in range(notes_count):
            if (random.randint(1, 11) % 7 == 0):  # drop notes randomly
                pause_note = note.Rest()
                pause_note.duration.quarterLength = current_duration
                right_hand.append(pause_note)
                continue

            # add a chord instead of a single note
            if (random.randint(0, 4) % 3 == 0):
                random_index = random.randint(0, len(right_hand_chords) - 1)
                random_chord = right_hand_chords[random_index].copy()
                newChord = chord.Chord(
                    random_chord, quarterLength=current_duration)
                newChord.volume.velocity = velocity
                right_hand.append(newChord)
                continue
            
            random_note = right_hand_notes[random.randint(0, len(right_hand_notes) - 1)]
            my_note = note.Note(random_note, quarterLength=current_duration)
            my_note.volume.velocity = velocity
            right_hand.append(my_note)

        # Generate notes for the left hand
        for note_i in range(12):
            if (random.randint(0, 7) == 5):
                pause_note = note.Rest()
                pause_note.duration.quarterLength = 0.25
                left_hand.append(pause_note)
                continue
            k: int = random.randint(0, len(new_song_generator.baselines) - 1)
            new_note = note.Note(new_song_generator.baselines[k][note_i], quarterLength=0.25)
            new_note.volume.velocity = volumes[note_i]
            left_hand.append(new_note)

    # Generate music
    while right_hand.duration.quarterLength < quarters_count:
        add_one_interval()

    # Combine hands into stream
    myStream = stream.Stream([right_hand, left_hand])
    myStream.metadata = metadata.Metadata()
    myStream.metadata.title = "Waltz"
    myStream.metadata.composer = "RESO"
    # Write to MIDI and PDF file
    filepath_midi = os.path.join("generated_data", f"{filename}.mid")
    filepath_pdf = os.path.join("generated_data", f"{filename}.pdf")
    myStream.write('midi', fp=filepath_midi)
    myStream.write('musicxml.pdf', fp=filepath_pdf)

    # For this download MuseScore 3
    # myStream.show()
if __name__ == '__main__':
    generate_music03(64, 'example.midi')