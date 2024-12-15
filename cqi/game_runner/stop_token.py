import time


class StopToken:
    def __init__(self):
        self._is_canceled = False

    def is_canceled(self) -> None:
        return self._is_canceled

    def cancel(self, *kargs) -> None:
        self._is_canceled = True
        print("Stopping...")

    def wait(self, duration: int) -> bool:
        for _ in range(duration):
            time.sleep(1)
            if (self.is_canceled()):
                return False

        return True
