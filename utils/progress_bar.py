import time


class ProgressBar:
    """
    Should be initialized with the start time of the tracked process, the
    target value of it, the displayed message and the desired length of
    the progress bar in the terminal (optional, defaults to 20).
    """
    def __init__(self, start_time: time, target, message: str, bar_length=20):
        self.start_time = start_time
        self.target = target
        self.message = message
        self.bar_length = bar_length

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
        except ZeroDivisionError:
            print('Generating: [%s%s] %d%% ~ ETA inf'
                  % (arrow, spaces, percent), end='\r')

    def end(self, end_message: str):
        print(end_message + ' ' *
              (len(self.message) + self.bar_length - len(end_message) + 25))