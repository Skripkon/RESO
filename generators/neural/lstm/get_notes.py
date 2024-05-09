import os
import threading

from music21 import bar, chord, clef, converter, metadata, meter, note, tempo


class NotesParser:
    """
    The only parameter for initialization is a string that represents a path.
    It could be a path to either a file (.mid) or a directory
    containing such files.
    """
    previos_note: dict = {"D": "C",  # this dict is only needed
                          "E": "D",  # to eliminate flat symbols
                          "G": "F",
                          "A": "G",
                          "B": "A"}

    def __init__(self, path):
        self.notes_mutex = threading.Lock()
        self.folder_path = None
        self.file_path = None
        self.files_parsed = 0
        self.files_parsed_mutex = threading.Lock()

        if os.path.isdir(path):
            self.folder_path = path

        elif os.path.isfile(path):
            self.file_path = path

        else:
            raise Exception("Pass a path to either a folder or a file.")

    @staticmethod
    def eliminate_flat_symbol(pitch: str) -> str:
        """
        Args:
            pitch (str): pitch with a flat symbol

        Returns:
            str: the same pitch, but wihout a flat symbol
        """

        match pitch[0]:
            case "C":
                return "B"
            case "F":
                return "E"
            case _:
                return NotesParser.previos_note[pitch[0]] + "#"

    @staticmethod
    def format_note(note) -> str:
        pitch = str(note)[0:-1]
        octave = str(note)[-1]
        if "-" in pitch:
            pitch = NotesParser.eliminate_flat_symbol(pitch)
        if int(octave) < 3:
            return pitch + '3'
        if int(octave) > 5:
            return pitch + '5'
        return pitch + octave

    @staticmethod
    def remove_leading_rests(lst):
        while lst and NotesParser.classify_element(lst[0]) in ['rest',
                                                               'useless']:
            lst.pop(0)
        return lst

    @staticmethod
    def classify_element(e) -> str:
        if isinstance(e, note.Note):
            return "note"
        if isinstance(e, chord.Chord):
            return "chord"
        if (isinstance(e, bar.Barline) or
                isinstance(e, clef.TrebleClef) or
                isinstance(e, meter.base.TimeSignature) or
                isinstance(e, tempo.MetronomeMark) or
                isinstance(e, clef.BassClef) or
                isinstance(e, metadata.Metadata) or
                isinstance(e, note.Rest)):
            return "useless"

    @staticmethod
    def format_chord(chord):
        new_chord = set()
        chord_pitches = set()
        for n in sorted(chord.pitches):
            n = NotesParser.format_note(n)
            note_octave = int(n[-1])
            note_pitch = n[0:-1]
            if note_pitch in chord_pitches:
                continue
            if note_octave < 3:
                new_chord.add(note_pitch + '3')
            elif note_octave > 4:
                new_chord.add(note_pitch + '4')
            else:
                new_chord.add(note_pitch + str(note_octave))
            chord_pitches.add(note_pitch)

        result = sorted(list(new_chord))

        if len(result) > 1:
            return '.'.join([str(n) for n in result])
        elif len(result) == 1:
            if int(result[0][-1]) <= 3:
                return result[0][0:-1] + '4'
            else:
                return result[0]

        raise Exception("EMPTY CHORD")

    def process_files(self, start, end):
        temp_notes = []
        for file in self.files[start:end]:
            with self.files_parsed_mutex:
                self.files_parsed += 1
                print(
                    f"{self.files_parsed}/{len(self.files)} "
                    f"{os.path.basename(file)}"
                )
            midi = converter.parse(file)
            elements_to_parse = midi.flatten()
            for e in self.remove_leading_rests(elements_to_parse):
                element_type = self.classify_element(e)
                if element_type == "note":
                    temp_notes.append(self.format_note(e.pitch))
                elif element_type == "chord":
                    form_chord = self.format_chord(e)
                    form_chord_len = len(form_chord.split('.'))
                    if form_chord_len < 5:
                        temp_notes.append(form_chord)
                elif element_type == "rest":
                    temp_notes.append("Rest")
                elif element_type == "useless":
                    continue
                else:
                    print(f"Unhandled type {type(e)}")
        with self.notes_mutex:
            self.notes.extend(temp_notes)

    def get_notes_from_files(self) -> list:
        """
        Gets the sequence of all notes and chords from the MIDI files in the
        specified directory. Parses chords by joining their notes with '.',
        i.e. E G B -> E.G.B and rest notes are parsed as 'Rest'.
        """

        if self.folder_path is not None:
            self.files = [
                os.path.join(self.folder_path, file)
                for file in os.listdir(self.folder_path)
                if file.endswith('.mid')
            ]
            print(
                f"Parsing {len(self.files)} files from "
                f"{os.path.basename(self.folder_path)}"
            )
        else:
            if self.file_path.endswith('.mid'):
                self.files = [self.file_path]
                print("Parsing 1 file.")
            else:
                raise Exception("File is not .mid")

        self.notes = []
        thread_list = []

        num_threads = 16  # It's better to find out this number
        # based on a computer that runs the code, but it's fine for now

        # Calculate the number of files per thread
        files_per_thread = len(self.files) // num_threads

        # Create and start threads
        for i in range(num_threads):
            start = i * files_per_thread
            end = start + files_per_thread if i < num_threads - \
                1 else len(self.files)
            thread = threading.Thread(
                target=self.process_files, args=(start, end))
            thread.start()
            thread_list.append(thread)

        # Wait for all threads to complete
        for thread in thread_list:
            thread.join()

        return self.notes
