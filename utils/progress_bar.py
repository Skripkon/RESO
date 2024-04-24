import time
import redis


class ProgressBar:
    """
    Should be initialized with the start time of the tracked process, the
    target value of it, the displayed message and the desired length of
    the progress bar in the terminal (optional, defaults to 20). Also recieves
    the Redis object to communicate the front of the progress.
    """
    def __init__(self, start_time: time,
                 target,
                 message: str,
                 db: redis.Redis,
                 bar_length=20):
        self.start_time = start_time
        self.target = target
        self.message = message
        self.db = db
        self.bar_length = bar_length
        self.db.set('progress', 0)

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
            self.db.set("progress", float(percent / 100))
        except ZeroDivisionError:
            print('Generating: [%s%s] %d%% ~ ETA inf'
                  % (arrow, spaces, percent), end='\r')

    def end(self, end_message: str):
        self.db.set('progress', 1)
        print(end_message + ' ' *
              (len(self.message) + self.bar_length - len(end_message) + 25))
