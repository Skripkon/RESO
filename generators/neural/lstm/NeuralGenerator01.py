import os
import pickle
import time

from keras.models import load_model
import music21
import numpy as np
from utils.progress_bar import ProgressBar
from utils.scale import fix_scale


def generate_neural01(composer: str,
                      model_path: str,
                      duration: int,
                      tempo: str,
                      filename: str,
                      correct_scale: bool = True,
                      progress_map: dict = None
                      ):
    """
    Generates and saves as 'filename' a midi file using given model, duration
    and tempo. Composer argument instructs the function which folder to take
    notes file from. The generated track is also corrected to fit the scale
    better if the corresponding option is selected.
    """
    TEMPO_MAP = {'Normal': 100, 'Slow': 60, 'Fast': 120}
    COMPOSERS = ['Mozart', 'Bach', 'Chopin']
    SEQUENCE_LENGTH = 100

    assert composer in COMPOSERS and duration in range(30, 160)
    bpm = TEMPO_MAP.get(tempo, TEMPO_MAP['Normal'])
    quarters = duration * (bpm / 60)

    composer_data_path = os.path.join('data', composer)
    notes = []
    notes_file_path = os.path.join(composer_data_path, 'notes')
    with open(notes_file_path, 'rb') as notes_file:
        notes = pickle.load(notes_file)

    unique_notes = sorted(set(notes))
    note_to_int = dict((note, number) for number, note in
                       enumerate(unique_notes))
    int_to_note = dict((number, note) for number, note in
                       enumerate(unique_notes))

    input_sequences = []

    for i in range(len(notes) - SEQUENCE_LENGTH):
        sequence_in = notes[i:i + SEQUENCE_LENGTH]
        input_sequences.append([note_to_int[char] for char in sequence_in])

    filepath_midi = os.path.join("generated_data", f"{filename}.mid")

    model = load_model(model_path)

    start_index = np.random.randint(0, len(input_sequences) - 1)
    pattern = input_sequences[start_index]
    prev_pred_element = None
    pred_element = None

    # is just used to count time to fill the required duration
    count_stream = music21.stream.Stream()
    count_stream.insert(0, music21.tempo.MetronomeMark(number=bpm))
    shift = 0
    quarter_length = 0
    generated_notes = []
    generated_notes_lengths = []
    progress_bar = ProgressBar(start_time=time.time(),
                               target=quarters,
                               message='Generating:',
                               filename=filename,
                               progress_map=progress_map,
                               bar_length=40)
    while count_stream.quarterLength < quarters and \
            count_stream.quarterLength + quarter_length < quarters:

        progress_bar.update(count_stream.quarterLength, time.time())
        input_sequence = np.reshape(pattern, (1, len(pattern), 1))
        input_sequence = input_sequence / float(len(unique_notes))

        prev_pred_element = pred_element
        prediction = model.predict(input_sequence, verbose=0)
        pred_element_index = np.argmax(prediction)
        pred_element = int_to_note[pred_element_index]

        pattern.append(pred_element_index)
        pattern = pattern[1:]

        if prev_pred_element is None:
            continue
        if pred_element == prev_pred_element:
            quarter_length += 0.3
            continue

        generated_notes.append(prev_pred_element)
        generated_notes_lengths.append(quarter_length)

        if '.' in prev_pred_element:  # Сhord
            chord_notes_str = prev_pred_element.split('.')
            chord_notes = [music21.note.Note(n) for n in chord_notes_str]
            for i, chord_note in enumerate(chord_notes_str):
                chord_notes[i].pitch = music21.pitch.Pitch(chord_note)
            chord = music21.chord.Chord(chord_notes,
                                        quarterLength=quarter_length)
            count_stream.insert(shift, chord)
        else:  # Note
            note = music21.note.Note(prev_pred_element,
                                     quarterLength=quarter_length)
            count_stream.insert(shift, note)
        shift += 0.3
        quarter_length = 0

    print("Updating to 100%")
    progress_bar.update(current=quarters, cur_time=time.time())

    # Now we make the actual stream that will be rendered
    final_stream = music21.stream.Stream()
    final_stream.insert(0, music21.tempo.MetronomeMark(number=bpm))
    fixed_generated_notes = (fix_scale(generated_notes) if correct_scale
                             else generated_notes)
    shift = 0

    for ind, element in enumerate(fixed_generated_notes):
        if '.' in element:  # chord
            chord_notes_str = element.split('.')
            chord_notes = [music21.note.Note(n) for n in chord_notes_str]
            for i, chord_note in enumerate(chord_notes_str):
                chord_notes[i].pitch = music21.pitch.Pitch(chord_note)
            chord = music21.chord.Chord(
                chord_notes, quarterLength=generated_notes_lengths[ind])
            chord.volume.velocity = np.random.randint(80, 90)
            final_stream.insert(shift, chord)
        else:
            note = music21.note.Note(element, quarterLength=quarter_length)
            note.volume.velocity = np.random.randint(50, 70)
            final_stream.insert(shift, note)
        shift += 0.3

    final_stream.write('midi', fp=filepath_midi)

    progress_bar.end()
