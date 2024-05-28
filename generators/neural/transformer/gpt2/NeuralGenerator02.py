import os
import random
import time

import note_seq
from transformers import AutoTokenizer, GPT2LMHeadModel
from utils.progress_bar import ProgressBar

from .Decode import token_sequence_to_note_sequence


def generate_neural02(composer: str,
                      model_path: str,
                      duration: int,
                      tempo: str,
                      filename: str,
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

    assert composer in COMPOSERS and duration in range(30, 160)
    bpm = TEMPO_MAP.get(tempo, TEMPO_MAP['Normal'])

    # TODO
    quarters = 10

    filepath_midi = os.path.join("generated_data", f"{filename}.mid")

    model = GPT2LMHeadModel.from_pretrained(model_path, device_map='cpu')
    tokenizer = AutoTokenizer.from_pretrained(model_path, device_map='cpu') 

    progress_bar = ProgressBar(start_time=time.time(),
                               target=quarters,
                               message='Generating:',
                               filename=filename,
                               progress_map=progress_map,
                               bar_length=40)

    all_tokens = []
    input_ids = tokenizer.encode("PIECE_START GENRE=OTHER", return_tensors="pt") 
    additional_tokens = 2048
    number_of_regenerations = 4
    for i in range(number_of_regenerations):
        generated_ids = model.generate(
            input_ids,
            max_length=input_ids.shape[1] + additional_tokens,
            do_sample=True,
            temperature=0.75,
            eos_token_id=tokenizer.encode("TRACK_END")[0]
        )
        all_tokens += list(generated_ids[0][:-20])
        input_ids = generated_ids[:, -20:-1]
    all_tokens += list(generated_ids[0])
    token_sequence = tokenizer.decode(all_tokens)
    note_sequence = token_sequence_to_note_sequence(token_sequence, qpm=bpm)

    seconds_per_beat = 60.0 / bpm
    current_time = 0.0
    prev_end = 0.0
    durations = [1, 1.3, 1.7, 2]

    for note in note_sequence.notes:
        current_time = note.end_time
        if current_time > duration:
            note.start_time = current_time
            note.end_time = current_time
            continue
        generated_duration = note.end_time - note.start_time
        if prev_end < note.start_time:
            note.start_time = prev_end
        duration_seconds = random.choice(durations)
        duration_beats = duration_seconds * seconds_per_beat
        if generated_duration < duration_beats * seconds_per_beat:
            note.end_time = note.start_time + duration_beats
        prev_end = note.end_time


    print("Updating to 100%")
    progress_bar.update(current=quarters, cur_time=time.time())

    note_seq.sequence_proto_to_midi_file(note_sequence, filepath_midi)

    progress_bar.end()


# generate_neural02("Bach", "path", 60, "Slow", "123")
