import numpy as np


class Distortion:
    def __init__(self, sr=44100):
        self.sr = sr
        self.drive = 1.0
        self.mix = 1.0
        self.output_db = 0.0
        self.type = 'soft'  # soft, hard, tube, fuzz
        self.bypass = False

    def process(self, buffer):
        if self.bypass:
            return
        output_gain = 10 ** (self.output_db / 20)
        dry = buffer.copy()
        wet = buffer * self.drive

        if self.type == 'soft':
            wet = np.tanh(wet)
        elif self.type == 'hard':
            wet = np.clip(wet, -1, 1)
        elif self.type == 'tube':
            wet = np.sign(wet) * (1 - np.exp(-np.abs(wet) * 2))
            wet = np.tanh(wet * 1.5)
        elif self.type == 'fuzz':
            wet = np.clip(wet * 3, -1, 1)
            wet = np.sign(wet) * (1 - np.exp(-np.abs(wet) * 5))

        wet = wet * output_gain
        buffer[:] = dry * (1 - self.mix) + wet * self.mix

    def reset(self):
        pass

    @staticmethod
    def params():
        return {
            'type': {'options': ['soft', 'hard', 'tube', 'fuzz'], 'default': 'soft', 'label': 'Type'},
            'drive': {'min': 0.0, 'max': 10.0, 'default': 1.0, 'label': 'Drive'},
            'mix': {'min': 0.0, 'max': 1.0, 'default': 1.0, 'label': 'Mix'},
            'output_db': {'min': -24, 'max': 24, 'default': 0, 'label': 'Output', 'unit': 'dB'},
        }
