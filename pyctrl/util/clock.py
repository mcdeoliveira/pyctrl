from threading import Thread, Event


class Clock(Thread):
    """Call a function after a specified number of seconds and repeat:
            t = Timer(30.0, f, args=None, kwargs=None)
            t.start()
            t.cancel()     # stop the timer's action if it's still waiting
        Works similarly to the threading.Timer.
    """

    def __init__(self, interval, function, args=None, kwargs=None):
        super().__init__(self)
        self.interval = interval
        self.function = function
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self.running = False
        self.finished = Event()

    def cancel(self):
        """Stop the clock if it hasn't finished yet."""
        self.finished.set()

    def join(self):
        if self.running:
            self._finished.wait()
            super().join()

    def run(self):
        self.running = True
        while self.running:
            self.finished.wait(self.interval)
            if self.finished.is_set():
                # cancel has been called, should terminate
                self.running = False
                break
            else:
                # run function
                self.function(*self.args, **self.kwargs)
            # clear and repeat
            self.finished.clear()
