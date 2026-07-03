import numpy as np
import math


class FilterEQ:
    def __init__(self, sr=44100):
        self.sr = sr
        self.freq = 1000.0
        self.q = 0.707
        self.gain_db = 0.0
        self.type = 'LP'  # LP, HP, BP, Notch, LowShelf, HighShelf, Peak
        self.bypass = False

        self._b0 = self._b1 = self._b2 = 0.0
        self._a1 = self._a2 = 0.0
        self._x1 = self._x2 = 0.0
        self._y1 = self._y2 = 0.0
        self._update_coeffs()

    def _update_coeffs(self):
        w0 = 2 * math.pi * self.freq / self.sr
        cos_w = math.cos(w0)
        sin_w = math.sin(w0)
        alpha = sin_w / (2 * self.q)
        A = 10 ** (self.gain_db / 40)

        if self.type == 'LP':
            self._b0 = (1 - cos_w) / 2
            self._b1 = 1 - cos_w
            self._b2 = (1 - cos_w) / 2
            self._a0 = 1 + alpha
            self._a1 = -2 * cos_w
            self._a2 = 1 - alpha
        elif self.type == 'HP':
            self._b0 = (1 + cos_w) / 2
            self._b1 = -(1 + cos_w)
            self._b2 = (1 + cos_w) / 2
            self._a0 = 1 + alpha
            self._a1 = -2 * cos_w
            self._a2 = 1 - alpha
        elif self.type == 'BP':
            self._b0 = alpha
            self._b1 = 0.0
            self._b2 = -alpha
            self._a0 = 1 + alpha
            self._a1 = -2 * cos_w
            self._a2 = 1 - alpha
        elif self.type == 'Notch':
            self._b0 = 1
            self._b1 = -2 * cos_w
            self._b2 = 1
            self._a0 = 1 + alpha
            self._a1 = -2 * cos_w
            self._a2 = 1 - alpha
        elif self.type == 'LowShelf':
            if A == 1:
                A = 1.001
            beta = math.sqrt(A) / A * math.sqrt((A + 1) - (A - 1) * cos_w) if A > 0 else 1
            self._b0 = A * ((A + 1) - (A - 1) * cos_w + beta * (A - 1) + beta * (A + 1) * cos_w)
            self._b1 = -2 * A * ((A - 1) - (A + 1) * cos_w)
            self._b2 = A * ((A + 1) - (A - 1) * cos_w - beta * (A - 1) - beta * (A + 1) * cos_w)
            self._a0 = (A + 1) + (A - 1) * cos_w + beta * (A - 1) + beta * (A + 1) * cos_w
            self._a1 = -2 * ((A - 1) + (A + 1) * cos_w)
            self._a2 = (A + 1) + (A - 1) * cos_w - beta * (A - 1) - beta * (A + 1) * cos_w
        elif self.type == 'HighShelf':
            if A == 1:
                A = 1.001
            beta_side = math.sqrt(2 * A) if A > 0 else 1
            self._b0 = A * ((A + 1) + (A - 1) * cos_w + beta_side * (A - 1) - beta_side * (A + 1) * cos_w)
            self._b1 = 2 * A * ((A - 1) + (A + 1) * cos_w)
            self._b2 = A * ((A + 1) + (A - 1) * cos_w - beta_side * (A - 1) + beta_side * (A + 1) * cos_w)
            self._a0 = (A + 1) - (A - 1) * cos_w + beta_side * (A - 1) - beta_side * (A + 1) * cos_w
            self._a1 = 2 * ((A - 1) - (A + 1) * cos_w)
            self._a2 = (A + 1) - (A - 1) * cos_w - beta_side * (A - 1) + beta_side * (A + 1) * cos_w
        elif self.type == 'Peak':
            self._b0 = 1 + alpha * A
            self._b1 = -2 * cos_w
            self._b2 = 1 - alpha * A
            self._a0 = 1 + alpha / A
            self._a1 = -2 * cos_w
            self._a2 = 1 - alpha / A
        else:
            return

        inv_a0 = 1.0 / self._a0
        self._b0 *= inv_a0
        self._b1 *= inv_a0
        self._b2 *= inv_a0
        self._a1 *= inv_a0
        self._a2 *= inv_a0

    def update(self):
        self._update_coeffs()

    def process(self, buffer):
        if self.bypass:
            return
        b0, b1, b2 = self._b0, self._b1, self._b2
        a1, a2 = self._a1, self._a2
        x1, x2 = self._x1, self._x2
        y1, y2 = self._y1, self._y2

        for i in range(len(buffer)):
            x0 = buffer[i]
            y0 = b0 * x0 + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
            buffer[i] = y0
            x2, x1 = x1, x0
            y2, y1 = y1, y0

        self._x1, self._x2 = x1, x2
        self._y1, self._y2 = y1, y2

    def reset(self):
        self._x1 = self._x2 = 0.0
        self._y1 = self._y2 = 0.0

    @staticmethod
    def params():
        return {
            'type': {'options': ['LP', 'HP', 'BP', 'Notch', 'LowShelf', 'HighShelf', 'Peak'], 'default': 'LP', 'label': 'Type', 'show_readout': False},
            'freq': {'min': 20, 'max': 20000, 'default': 1000, 'label': 'Freq', 'unit': 'Hz', 'show_readout': True},
            'q': {'min': 0.1, 'max': 20, 'default': 0.707, 'label': 'Q', 'show_readout': True, 'range_dots': True},
            'gain_db': {'min': -24, 'max': 24, 'default': 0, 'label': 'Gain', 'unit': 'dB', 'show_readout': True},
        }
