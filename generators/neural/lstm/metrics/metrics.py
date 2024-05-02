from music21 import *
import pickle
from keras.models import load_model
import numpy as np


def calculate_note_difference(note_name1, note_name2):
    n1 = note.Note(note_name1)
    n2 = note.Note(note_name2)
    interval_semitones = interval.notesToInterval(n1, n2).semitones
    return abs(interval_semitones)


def calculate_chord_similarity(chord_a, chord_b):
    smaller_chord = chord_a
    larger_chord = chord_b
    if len(chord_a) > len(chord_b):
        smaller_chord = chord_b
        larger_chord = chord_a
    max_similarities = [0 for _ in range(len(smaller_chord))]
    for i in range(len(smaller_chord)):
        for note in larger_chord:
            similarity = 1 - (calculate_note_difference(smaller_chord[i], note) / 24)
            if similarity > max_similarities[i]:
                max_similarities[i] = similarity
    similarity = 1
    for val in max_similarities:
        similarity *= val
    return similarity


def calculate_chord_similarity_with_mae(chord_a, chord_b):
    total_error = 0
    for note_a in chord_a:
        for note_b in chord_b:
            total_error += calculate_note_difference(note_a, note_b)
    mean_absolute_error = total_error / (len(chord_a) * len(chord_b))
    return mean_absolute_error


def compare_elements(element1, element2):
    if ('.' in element1) and ('.' in element2):
        chord1_notes = element1.split('.')
        chord2_notes = element2.split('.')
        return 1 - (calculate_chord_similarity(chord1_notes, chord2_notes) / 24)
    elif ('.' in element1) or ('.' in element2):
        return 0
    else:
        return 1 - (calculate_note_difference(element1, element2) / 24)


def calculate_noteslist_similarity(list1, list2):
    total_similarity = 0
    for i in range(len(list1)):
        total_similarity += compare_elements(list1[i], list2[i])
    average_similarity = total_similarity / len(list1)
    return average_similarity


def calculate_similarity(notes_path, model_path, N, index):
    # Load notes from file
    with open(notes_path, 'rb') as notes_file:
        notes = pickle.load(notes_file)
        
    SEQUENCE_LENGTH = 100

    # Create input sequences and corresponding output
    unique_notes = sorted(set(notes))
    note_to_int = dict((note, number) for number, note in enumerate(unique_notes))
    int_to_note = dict((number, note) for number, note in enumerate(unique_notes))

    input_sequences = []
    output_sequences = []

    for i in range(len(notes) - SEQUENCE_LENGTH):
        sequence_in = notes[i:i + SEQUENCE_LENGTH]
        sequence_out = notes[i + SEQUENCE_LENGTH]
        input_sequences.append([note_to_int[char] for char in sequence_in])
        output_sequences.append(note_to_int[sequence_out])

    # Load the model
    model = load_model(model_path)

    # Variables for similarity calculation
    total_similarity = 0
    similarity_list = []

    pattern = input_sequences[index].copy()

    # Skip first SEQUENCE_LENGTH
    for i in range(SEQUENCE_LENGTH):
        input_sequence = np.reshape(pattern, (1, len(pattern), 1))
        input_sequence = input_sequence / float(len(unique_notes))
        prediction = model.predict(input_sequence, verbose=0)
        pred_element_index = np.argmax(prediction)
        pattern.append(pred_element_index)
        pattern = pattern[1:]

    expected_notes = [int_to_note[k] for k in input_sequences[index + SEQUENCE_LENGTH]]
    predict_notes = [int_to_note[k] for k in pattern]


    for i in range(N):
        input_sequence = np.reshape(pattern, (1, len(pattern), 1))
        input_sequence = input_sequence / float(len(unique_notes))

        # Predict
        prediction = model.predict(input_sequence, verbose=0)
        pred_element_index = np.argmax(prediction)
        pattern.append(pred_element_index)
        pattern = pattern[1:]

        expected_notes.append(int_to_note[output_sequences[index + i + SEQUENCE_LENGTH]])
        predict_notes.append(int_to_note[pred_element_index])
        expected_notes = expected_notes[1:]
        predict_notes = predict_notes[1:]

        # Calculate similarity
        similarity = calculate_noteslist_similarity(expected_notes, predict_notes)
        similarity_list.append(similarity)
        total_similarity += similarity

    # Return similarity list and average similarity
    return similarity_list, total_similarity / N

            

