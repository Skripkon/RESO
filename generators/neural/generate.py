import numpy as np
import music21

def generate(model, input_sequences, int_to_note, unique_notes, output_filename, number_of_notes_to_generate):
    start_index = np.random.randint(0, len(input_sequences) - 1)
    pattern = input_sequences[start_index]
    prediction_output = []

    for i in range(number_of_notes_to_generate):
        input_sequence = np.reshape(pattern, (1, len(pattern), 1))
        input_sequence = input_sequence / float(len(unique_notes))

        prediction = model.predict(input_sequence, verbose=0)
        index = np.argmax(prediction)
        result = int_to_note[index]
        
        print(f"Iteration {i+1}/{number_of_notes_to_generate} | Generated Note: {result}")
        
        prediction_output.append(result)
        pattern.append(index)
        pattern = pattern[1:]

    # Convert output to MIDI file
    myStream = music21.stream.Stream()
    shift = 0
    quarterLength = 0

    prev_pattern = prediction_output[0]

    for ind in range(1, len(prediction_output)):
        pattern = prediction_output[ind]
        if pattern == prev_pattern:
            quarterLength += 0.3
            continue 
        if '.' in prev_pattern:  # Сhord
            notes_in_chord = prev_pattern.split('.') 
            chord_notes = [music21.note.Note(n) for n in notes_in_chord]
            for i, note_in_chord in enumerate(notes_in_chord):
                chord_notes[i].pitch = music21.pitch.Pitch(note_in_chord)
            chord = music21.chord.Chord(chord_notes, quarterLength=quarterLength)
            chord.volume.velocity = np.random.randint(90, 100)
            myStream.insert(shift, chord)
            shift += 0.3
            quarterLength = 0
        else:  # Note
            note = music21.note.Note(prev_pattern, quarterLength=quarterLength)
            note.volume.velocity = np.random.randint(70, 80)
            myStream.insert(shift, note) 
            shift += 0.3
            quarterLength = 0
        prev_pattern = pattern

    myStream.write('midi', fp=output_filename)
