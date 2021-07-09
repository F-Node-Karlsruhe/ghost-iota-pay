import threading


class AtomicCounter:
    """
    An atomic, thread-safe incrementing counter.
    """
    def __init__(self, initial=0):
        """Initialize a new atomic counter to given initial value (default 0)."""
        self.value = initial
        self._lock = threading.Lock()

    def increment(self, num=1):
        """Atomically increment the counter by num (default 1) and return the
        new value.
        """
        with self._lock:
            self.value += num
            return self.value

    def decrement(self, num=1):
        """Atomically decrement the counter by num (default 1) and return the
        new value.
        """
        with self._lock:
            self.value -= num
            return self.value
            