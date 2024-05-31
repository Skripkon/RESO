import os
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
    notes file from.
    """
    TEMPO_MAP = {"Normal": 100, "Slow": 60, "Fast": 120}
    COMPOSERS = ["Mozart", "Bach", "Chopin"]

    assert composer in COMPOSERS and duration in range(30, 160)
    bpm = TEMPO_MAP.get(tempo, TEMPO_MAP["Normal"])
    NOTE_LENGTH = 0.25 * 60 / bpm
    BAR_LENGTH = 4.0 * 60 / bpm

    filepath_midi = os.path.join("generated_data", f"{filename}.mid")

    model = GPT2LMHeadModel.from_pretrained(model_path, device_map="cpu")
    tokenizer = AutoTokenizer.from_pretrained(model_path, device_map="cpu")

    # Generating
    all_tokens = []
    input_ids = tokenizer.encode(
        "PIECE_START TIME_SIGNATURE=4_4 GENRE=OTHER TRACK_START", return_tensors="pt"
    )
    additional_tokens = 2048
    last_tokens_index = 0
    last_tokens_len = 0
    i = 0
    progress_bar = ProgressBar(start_time=time.time(),
                               target=duration,
                               message='Generating:',
                               filename=filename,
                               progress_map=progress_map,
                               bar_length=40)
    while 0.1 * NOTE_LENGTH * len(all_tokens) < duration:
        progress_bar.update(0.1 * NOTE_LENGTH * len(all_tokens), time.time())
        if last_tokens_index > 1 and last_tokens_len == len(all_tokens):
            all_tokens = []
            input_ids = tokenizer.encode(
                "PIECE_START TIME_SIGNATURE=4_4 GENRE=OTHER TRACK_START",
                return_tensors="pt",
            )
            last_tokens_index = 0
            last_tokens_len = 0
            i = 0
            continue
        if last_tokens_len == len(all_tokens) and i != 0:
            last_tokens_index += 1
        if last_tokens_len != len(all_tokens):
            last_tokens_index = 0
            last_tokens_len = 0
        generated_ids = model.generate(
            input_ids,
            max_length=input_ids.shape[1] + additional_tokens,
            do_sample=True,
            temperature=0.75,
            eos_token_id=tokenizer.encode("TRACK_END")[0],
        )
        if i == 1:
            all_tokens = (
                list(
                    tokenizer.encode(
                        "PIECE_START TIME_SIGNATURE=4_4 GENRE=OTHER TRACK_START",
                        return_tensors="pt",
                    )[0]
                )
                + all_tokens
            )
        if i > 0:
            all_tokens += list(generated_ids[0][:-100])
        input_ids = generated_ids[:, -100:-1]
        i += 1
    all_tokens += list(generated_ids[0])
    token_sequence = tokenizer.decode(all_tokens)
    note_sequence = token_sequence_to_note_sequence(
        token_sequence, qpm=bpm, NOTE_LENGTH=NOTE_LENGTH, BAR_LENGTH=BAR_LENGTH
    )

    # Duration fixing
    prev_end = 0
    new_notes = []
    for note in note_sequence.notes:
        if note.start_time > duration:
            continue
        if note.end_time > duration:
            note.end_time = duration
            new_notes.append(note)
            continue
        if prev_end < note.start_time:
            note.start_time = prev_end
        prev_end = note.end_time
        new_notes.append(note)

    del note_sequence.notes[:]
    note_sequence.notes.extend(new_notes)
    note_sequence.total_time = duration
    print(note_sequence.total_time)

    progress_bar.update(current=duration, cur_time=time.time())

    # Coverting to midi
    note_seq.note_sequence_to_midi_file(note_sequence, filepath_midi)
    progress_bar.end()
