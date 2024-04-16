import numpy as np
import music21
import os
from keras.models import load_model
import pickle

tempo_map = {'Normal': 100, 'Slow': 60, 'Fast': 120}

def generate(model, input_sequences, int_to_note,
             unique_notes, output_filename, quarters, bpm):
    start_index = np.random.randint(0, len(input_sequences) - 1)
    pattern = input_sequences[start_index]
    prev_result = "-"
    result = "-"

    myStream = music21.stream.Stream()
    myStream.insert(0, music21.tempo.MetronomeMark(number=bpm))
    shift = 0
    quarterLength = 0

    while myStream.quarterLength < quarters:
        input_sequence = np.reshape(pattern, (1, len(pattern), 1))
        input_sequence = input_sequence / float(len(unique_notes))

        prediction = model.predict(input_sequence, verbose=0)
        index = np.argmax(prediction)
        prev_result = result
        result = int_to_note[index]

        pattern.append(index)
        pattern = pattern[1:]

        if prev_result == "-": 
            continue
        if myStream.quarterLength >= quarters:
            break
        if result == prev_result:
            quarterLength += 0.3
            continue
        if '.' in prev_result:  # Сhord
            notes_in_chord = prev_result.split('.')
            chord_notes = [music21.note.Note(n) for n in notes_in_chord]
            for i, note_in_chord in enumerate(notes_in_chord):
                chord_notes[i].pitch = music21.pitch.Pitch(note_in_chord)
            chord = music21.chord.Chord(chord_notes,
                                        quarterLength=quarterLength)
            chord.volume.velocity = np.random.randint(90, 100)
            myStream.insert(shift, chord)
            shift += 0.3
            quarterLength = 0
        else:  # Note
            note = music21.note.Note(prev_result, quarterLength=quarterLength)
            note.volume.velocity = np.random.randint(70, 80)
            myStream.insert(shift, note)
            shift += 0.3
            quarterLength = 0

    myStream.write('midi', fp=output_filename)

def generate_neural(composer, model_path, duration, tempo, name_of_the_file):

    bpm = tempo_map.get(tempo, tempo_map['Normal'])
    quarters = duration * (bpm / 60)

    SEQUENCE_LENGTH = 100

    DATA_PATH = f'/Users/nad/hse/2023-24/spring_proj2/MuseGen/data/{composer}'
    notes = []
    notes_file_path = os.path.join(DATA_PATH, 'notes')
    with open(notes_file_path, 'rb') as notes_file:
        notes = pickle.load(notes_file)

    unique_notes = sorted(set(notes))
    note_to_int = dict((note, number) for number, note in enumerate(unique_notes))
    int_to_note = dict((number, note) for number, note in enumerate(unique_notes))

    input_sequences = []

    for i in range(len(notes) - SEQUENCE_LENGTH):
        sequence_in = notes[i:i + SEQUENCE_LENGTH]
        input_sequences.append([note_to_int[char] for char in sequence_in])

    filepath_midi = os.path.join("generated_data", f"{name_of_the_file}.mid")

    model = load_model(model_path)

    generate(model, input_sequences=input_sequences, int_to_note=int_to_note, 
             unique_notes=unique_notes, output_filename=filepath_midi, 
             quarters=quarters, bpm=bpm)