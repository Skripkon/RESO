import time


class ProgressBar:
    """
    Should be initialized with the start time of the tracked process, the
    target value of it, the displayed message, name of the generated track
    and the desired length of the progress bar in the terminal (optional,
    defaults to 20). Also recieves the dictionary to communicate the front
    of the current progress of generation.
    """
    def __init__(self, start_time: time,
                 target,
                 message: str,
                 filename: int,
                 progress_map: dict,
                 bar_length=20):
        self.start_time = start_time
        self.target = target
        self.message = message
        self.filename = filename
        self.progress_map = progress_map
        self.bar_length = bar_length
        self.progress_map[filename] = 0

    def update(self, current, cur_time):
        percent = float(current) * 100 / self.target
        arrow = '-' * int(percent / 100 * self.bar_length - 1) + '>'
        spaces = ' ' * (self.bar_length - len(arrow))
        elapsed_time = cur_time - self.start_time
        try:
            est_time = (100 * elapsed_time) / percent
            print(f'''Generating: [%s%s] %d%% ~ ETA {self.start_time +
                                                    est_time -
                                                    cur_time:.1f} sec    '''
                  % (arrow, spaces, percent), end='\r')
            self.progress_map[self.filename] = float(percent / 100)
        except ZeroDivisionError:
            print('Generating: [%s%s] %d%% ~ ETA inf'
                  % (arrow, spaces, percent), end='\r')

    def end(self, end_message: str):
        self.progress_map[self.filename] = 1
        print(end_message + ' ' *
              (len(self.message) + self.bar_length - len(end_message) + 25))
