from time import sleep
from queue import Queue
from threading import Thread

INITIAL_INTERVAL = 1
MAX_INTERVAL = 60
CHECK_NUMBER = 10


class TaskManager:

    def __init__(self):
        self.interval = INITIAL_INTERVAL
        self.count = 0

    def dynamic_interval(self):
        sleep(self.interval)
        print(self.interval)
        self.count += 1

        # Increase check interval
        if self.count >= CHECK_NUMBER and self.interval < MAX_INTERVAL:
            self.interval += 5
            self.count = 0

    def main_loop(self):

        while True:
            try:
                self.dynamic_interval()

            except KeyboardInterrupt:
                break


if __name__ == '__main__':
    manager = TaskManager()
    manager.main_loop()
