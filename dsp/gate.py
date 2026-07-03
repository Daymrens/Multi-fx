import numpy as np


class Gate:
    def __init__(self, sr=44100):
        self.sr = sr
        self.threshold = -40.0
        self.attack_ms = 1.0
        self.hold_ms = 20.0
        self.release_ms = 50.0
        self.bypass = False

        self._envelope = 0.0
        self._hold_counter = 0
        self._attack_coeff = self._time_to_coeff(self.attack_ms)
        self._release_coeff = self._time_to_coeff(self.release_ms)
        self._hold_samples = int(self.hold_ms * sr / 1000)

    def _time_to_coeff(self, ms):
        if ms <= 0:
            return 1.0
        return 1.0 - np.exp(-1.0 / (ms * self.sr / 1000))

    def update(self):
        self._attack_coeff = self._time_to_coeff(self.attack_ms)
        self._release_coeff = self._time_to_coeff(self.release_ms)
        self._hold_samples = int(self.hold_ms * self.sr / 1000)

    def process(self, buffer):
        if self.bypass:
            return
        thr_linear = 10 ** (self.threshold / 20)
        n = len(buffer)
        for i in range(n):
            sample = buffer[i]
            abs_s = abs(sample)
            if abs_s > self._envelope:
                self._envelope += self._attack_coeff * (abs_s - self._envelope)
            else:
                self._envelope += self._release_coeff * (abs_s - self._envelope)

            if self._envelope > thr_linear:
                self._hold_counter = self._hold_samples
                gain = 1.0
            elif self._hold_counter > 0:
                self._hold_counter -= 1
                gain = 1.0
            else:
                gain = 0.0

            buffer[i] = sample * gain

    def reset(self):
        self._envelope = 0.0
        self._hold_counter = 0

    @staticmethod
    def params():
        return {
            'threshold': {'min': -80, 'max': 0, 'default': -40, 'label': 'Thresh', 'unit': 'dB'},
            'attack_ms': {'min': 0.1, 'max': 50, 'default': 1.0, 'label': 'Attack', 'unit': 'ms'},
            'hold_ms': {'min': 0, 'max': 200, 'default': 20, 'label': 'Hold', 'unit': 'ms'},
            'release_ms': {'min': 5, 'max': 500, 'default': 50, 'label': 'Release', 'unit': 'ms'},
        }
