import numpy as np


class Limiter:
    def __init__(self, sr=44100):
        self.sr = sr
        self.threshold = -0.5
        self.release_ms = 50.0
        self.lookahead_ms = 2.0
        self.bypass = False

        lookahead_samples = int(self.lookahead_ms * sr / 1000) + 1
        self._delay_buf = np.zeros(lookahead_samples)
        self._delay_idx = 0
        self._gain = 1.0
        self._peak = 0.0

    def process(self, buffer):
        if self.bypass:
            return
        thr = 10 ** (self.threshold / 20)
        release = 1.0 - np.exp(-1.0 / (self.release_ms * self.sr / 1000))
        lookahead = len(self._delay_buf)

        n = len(buffer)
        for i in range(n):
            delayed = self._delay_buf[self._delay_idx]
            self._delay_buf[self._delay_idx] = buffer[i]
            self._delay_idx = (self._delay_idx + 1) % lookahead

            future = buffer[min(i + lookahead, n - 1)]
            self._peak = max(self._peak, abs(future))
            self._peak += release * (0 - self._peak)

            target = 1.0
            if self._peak > thr:
                target = thr / max(self._peak, 1e-10)

            if target < self._gain:
                self._gain = target
            else:
                self._gain += release * (target - self._gain)

            buffer[i] = delayed * self._gain

    def reset(self):
        self._delay_buf.fill(0)
        self._delay_idx = 0
        self._gain = 1.0
        self._peak = 0.0

    @staticmethod
    def params():
        return {
            'threshold': {'min': -24, 'max': 0, 'default': -0.5, 'label': 'Ceiling', 'unit': 'dB'},
            'release_ms': {'min': 5, 'max': 500, 'default': 50, 'label': 'Release', 'unit': 'ms'},
            'lookahead_ms': {'min': 0, 'max': 10, 'default': 2, 'label': 'Lookahead', 'unit': 'ms'},
        }
