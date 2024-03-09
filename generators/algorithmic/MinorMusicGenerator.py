class MinorMusicGenerator:
    # notes in music21 are enumerated from 0 to 127
    # C4 (middle C) = 60
    # scale is a number from 59 (B) to 70 (Bb)
    def __init__(self, scale=60):
        self.minor_chords = None
        self.correct_notes = None
        self.baselines = None
        self.additional_chords = None
        # check if scale is integer and in a range of (59, 70)
        if not isinstance(scale, int):
            raise ValueError("scale must be an integer")
        elif scale < 59 or scale > 70:
            raise ValueError("scale must be in a range from 59 to 70")
        else:
            # If the scale is valid, it sets the scale attribute,
            # and then calls two methods:
            self.scale = scale
        self.correct_minor_chords()
        self.create_baselines()
        self.calculate_correct_notes()
        self.add_additional_chords()

    # calculates a list of corrected notes based on a predefined set of shifts.
    # store the result in the correct_notes attribute.
    def calculate_correct_notes(self):
        shifts = [0, 2, 3, 5, 7, 8, 10]
        notes = [(self.scale + shift) for shift in shifts]
        # all notes from this list shold be in a range from 58 to 69
        # (which is a 4th octave)
        for i in range(len(notes)):
            if notes[i] >= 70:
                notes[i] -= 12
        self.correct_notes = notes

    # creates a minor chord based on a given note
    @classmethod
    def get_minor_chord(cls, note):
        return [note, note + 3, note + 7]

    # creates three minor chords using the get_minor_chord method.
    # The chords are based on the current scale, shifted by specific values.
    # The resulting chords are stored in the minor_chords attribute.
    def correct_minor_chords(self):
        first_chord = self.get_minor_chord(self.scale - 12)
        second_chord = self.get_minor_chord(self.scale + 5 - 12)
        third_chord = self.get_minor_chord(self.scale + 7 - 12)
        self.minor_chords = [first_chord, second_chord, third_chord]

    # creates additional chords
    # The resulting chords are stored in the additional_chords attribute.
    def add_additional_chords(self):
        chord1 = [self.scale, self.scale + 3, self.scale + 7, self.scale + 8]
        chord2 = [self.scale - 2, self.scale +
                  2, self.scale + 5, self.scale + 8]
        chord3 = [self.scale + 2, self.scale +
                  5, self.scale + 8, self.scale + 12]
        chord4 = [self.scale + 2, self.scale + 5, self.scale + 7]
        chord5 = [self.scale, self.scale + 3, self.scale + 5]
        self.additional_chords = [chord1, chord2, chord3, chord4, chord5]

    # creates a sequence of notes for the left hand (12 notes)
    @staticmethod
    def create_one_baseline(scale):
        cur_note = scale - 24
        return [cur_note, cur_note + 3, cur_note + 7, cur_note + 12,
                cur_note + 15, cur_note + 19, cur_note + 24, cur_note + 19,
                cur_note + 15, cur_note + 12, cur_note + 7, cur_note + 3]

    # creates 3 different sequences of notes for the left hand (from I, IV, V)
    def create_baselines(self):
        first_baseline = self.create_one_baseline(self.scale)
        second_baseline = self.create_one_baseline(self.scale + 5)
        third_baseline = self.create_one_baseline(self.scale + 7)
        self.baselines = [first_baseline, second_baseline, third_baseline]
