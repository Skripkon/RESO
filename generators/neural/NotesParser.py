import os
import threading

from music21 import bar, chord, clef, converter, metadata, meter, note, tempo


class NotesParser:
    """
    Class to parse .mid files into python arrays of notes.
    """

    _previous_note: dict = {"D": "C",  # this dict is only needed
                            "E": "D",  # to eliminate flat symbols
                            "G": "F",
                            "A": "G",
                            "B": "A"}

    def __init__(self, path: str = None):
        """
        Initializes the NotesParser.

        Args:
            path (str, optional): A path to either a file (.mid) or a directory containing such files. Defaults to None.
        Raises:
            Exception: Provided path is not valid.
        """
        self.concatFiles = True
        self.max_files = 1e6
        self.files_parsed = 0
        self.folder_path = None
        self.file_path = None
        self.files = None
        self.notes_mutex = threading.Lock()
        self.files_parsed_mutex = threading.Lock()

        if path is not None:
            if os.path.isdir(path):
                self.folder_path = path

            elif os.path.isfile(path):
                self.file_path = path
            else:
                raise Exception("Provided path is not valid.")

    def _eliminate_flat_symbol(self, pitch: str) -> str:
        """
        Substitutes a flat symbol with '#' or deletes a flat symbol and changes the note (as in the case of F-flat and C-flat).

        Args:
            pitch (str): A pitch with a flat symbol.

        Returns:
            str: The same pitch but without a flat symbol.
        """

        if pitch[0] == "C":
            return "B"
        elif pitch[0] == "F":
            return "E"
        else:
            return self._previous_note[pitch[0]] + "#"

    def _format_note(self, note: str) -> str:
        """
        Formats the given note.

        Args:
            note (str): A raw note from a .mid file.

        Returns:
            str: A formatted note.
        """
        pitch = str(note)[0:-1]
        octave = str(note)[-1]
        if "-" in pitch:
            pitch = self._eliminate_flat_symbol(pitch)
        if int(octave) < 3:
            return pitch + '3'
        if int(octave) > 5:
            return pitch + '5'
        return pitch + octave

    def _remove_leading_rests(self, lst: list[str]) -> list[str]:
        """
        Removes leading rests from a given list of pitches.

        Args:
            lst (list[str]): A list of pitches.

        Returns:
            list[str]: A list of pitches without leading rests.
        """
        while lst and self._classify_element(lst[0]) in ['rest', 'useless']:
            lst.pop(0)
        return lst

    def _classify_element(self, e) -> str:
        """
        Determines the type of the music object.

        Args:
            e (object): Any music object to be classified.

        Returns:
            str: If it fails to classify the type, it returns 'useless'. Otherwise, it returns the specific type.
        """
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

    def _format_chord(self, chord: chord) -> str:
        """
        Formats the given chord.

        Args:
            chord (music21.chord): A raw chord from a .mid file.

        Raises:
            Exception: If the chord doesn't consist of any notes.

        Returns:
            str: A chord in the following format: Note_1.Note_2.<...>.Note_N, where N is the number of notes in the given chord.
        """
        new_chord = set()
        chord_pitches = set()
        for n in sorted(chord.pitches):
            n = self._format_note(n)
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

    def _process_files(self, start: int, end: int):
        """
        Processes files from `self.files[start]` to `self.files[end]`.
        Depending on the value of `self.concatFiles`, it behaves differently.

        Args:
            start (int): Start index.
            end (int): End index.
        """
        temp_notes = []
        for file in self.files[start:end]:
            with self.files_parsed_mutex:
                self.files_parsed += 1
                print(f"{self.files_parsed}/{len(self.files)} {os.path.basename(file)}")
            midi = converter.parse(file)
            elements_to_parse = midi.flatten()
            for e in self._remove_leading_rests(elements_to_parse):
                element_type = self._classify_element(e)
                if element_type == "note":
                    temp_notes.append(self._format_note(e.pitch))
                elif element_type == "chord":
                    form_chord = self._format_chord(e)
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
                if len(temp_notes) > 1:
                    if self.concatFiles:
                        self.notes.extend(temp_notes)
                    else:
                        self.notes.append(temp_notes)

    def get_notes_from_files(self, path: str = None, concatFiles: bool = True, max_files: int = 1e6, one_scale: bool = False) -> list:
        """
        Gets the sequence of all notes and chords from the MIDI files in the specified directory.

        If 'path' is specified, it processes files from this path. Otherwise, it checks for files from 'self.folder_path' or 'self.file_path'.
        If no file is specified, it raises an exception.

        Args:
            path (str, optional): A path to either a file (.mid) or a directory containing such files. Defaults to None.
            concatFiles (bool, optional): Determines how to process many files:
                - if `self.concatFiles` is set to False, then this is a list of lists, where each nested list represents a single file.
                - if `self.concatFiles` is set to True, then this is a list of str objects.
            max_files (int, optional): The maximum amount of files that could be parsed. Defaults to 1e6.
            one_scale (bool, optional). If one_scale is set to True, all compositions are transposed to one scale. Defaults to False.

        Raises:
            Exception: If the specified path is not valid or no path is specified during initialization of the Parser.

        Returns:
            list: The list of parsed pitches.
        """
        self.concatFiles = concatFiles
        self.max_files = max_files
        self.files_parsed = 0
        self.files = []
        if path is not None:
            if os.path.isdir(path):
                self.files = [os.path.join(path, file) for file in os.listdir(path) if file.endswith('.mid')]
                print(f"Parsing {len(self.files)} files from {os.path.basename(path)}")
            elif os.path.isfile(path):
                self.files = [path]
                print("Parsing 1 file.")
        else:
            if self.folder_path is not None:
                self.files = [os.path.join(self.folder_path, file) for file in os.listdir(self.folder_path) if file.endswith('.mid')]
                print(f"Parsing {len(self.files)} files from {os.path.basename(self.folder_path)}")
            elif self.file_path is not None:
                if self.file_path.endswith('.mid'):
                    self.files = [self.file_path]
                    print("Parsing 1 file.")
                else:
                    raise Exception("File is not .mid")
            else:
                raise Exception("You forgot to provide a path.")

        if len(self.files) > max_files:  # Take into account a possible constraint on the number of files to be processed.
            self.files = self.files[0: max_files]
        self.notes = []
        thread_list = []

        num_threads = 8
        # Calculate the number of files per thread
        files_per_thread = len(self.files) // num_threads
        if len(self.files) <= num_threads:  # special case
            num_threads = len(self.files)
            files_per_thread = 1

        # Create and start threads
        for i in range(num_threads):
            start = i * files_per_thread
            end = start + files_per_thread if i < num_threads - \
                1 else len(self.files)
            thread = threading.Thread(
                target=self._process_files, args=(start, end))
            thread.start()
            thread_list.append(thread)

        # Wait for all threads to complete
        for thread in thread_list:
            thread.join()

        return self.notes
