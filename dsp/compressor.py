import numpy as np


class Compressor:
    def __init__(self, sr=44100):
        self.sr = sr
        self.threshold = -20.0
        self.ratio = 4.0
        self.attack_ms = 5.0
        self.release_ms = 50.0
        self.knee_db = 6.0
        self.makeup_db = 3.0
        self.bypass = False

        self._envelope = 0.0

    def process(self, buffer):
        if self.bypass:
            return
        thr = 10 ** (self.threshold / 20)
        makeup = 10 ** (self.makeup_db / 20)
        knee = 10 ** (self.knee_db / 20)
        attack = 1.0 - np.exp(-1.0 / (self.attack_ms * self.sr / 1000))
        release = 1.0 - np.exp(-1.0 / (self.release_ms * self.sr / 1000))
        slope = 1.0 - 1.0 / self.ratio

        n = len(buffer)
        for i in range(n):
            abs_s = abs(buffer[i])
            if abs_s > self._envelope:
                self._envelope += attack * (abs_s - self._envelope)
            else:
                self._envelope += release * (abs_s - self._envelope)

            env_db = 20 * np.log10(max(self._envelope, 1e-10))
            diff = env_db - self.threshold

            if diff <= -self.knee_db / 2:
                gain_db = 0
            elif diff <= self.knee_db / 2:
                knee_start = self.threshold - self.knee_db / 2
                knee_diff = env_db - knee_start
                gain_db = slope * (knee_diff ** 2) / (2 * self.knee_db)
            else:
                gain_db = slope * diff

            gain = 10 ** (gain_db / 20) * makeup
            buffer[i] = buffer[i] * gain

    def reset(self):
        self._envelope = 0.0

    @staticmethod
    def params():
        return {
            'threshold': {'min': -60, 'max': 0, 'default': -20, 'label': 'Threshold', 'unit': 'dB'},
            'ratio': {'min': 1, 'max': 20, 'default': 4, 'label': 'Ratio'},
            'knee_db': {'min': 0, 'max': 12, 'default': 6, 'label': 'Knee', 'unit': 'dB'},
            'attack_ms': {'min': 0.1, 'max': 100, 'default': 5, 'label': 'Attack', 'unit': 'ms'},
            'release_ms': {'min': 5, 'max': 500, 'default': 50, 'label': 'Release', 'unit': 'ms'},
            'makeup_db': {'min': 0, 'max': 24, 'default': 3, 'label': 'Makeup', 'unit': 'dB'},
        }
