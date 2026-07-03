import numpy as np


class Modulation:
    def __init__(self, sr=44100):
        self.sr = sr
        self.rate_hz = 0.5
        self.depth = 0.5
        self.feedback = 0.0
        self.mix = 0.5
        self.mode = 'chorus'  # chorus, flanger, phaser
        self.bypass = False

        self._phase = 0.0
        self._buf_len = int(sr * 0.05)
        self._buffer = np.zeros(self._buf_len)
        self._write_idx = 0
        self._x1 = self._x2 = self._y1 = self._y2 = 0.0

    def process(self, buffer):
        if self.bypass:
            return
        n = len(buffer)
        out = np.zeros(n)

        for i in range(n):
            x = buffer[i]
            self._buffer[self._write_idx] = x
            lfo = 0.5 + 0.5 * np.sin(2 * np.pi * self.rate_hz * self._phase)

            if self.mode == 'chorus':
                delay_s = 0.005 + 0.020 * lfo * self.depth
            elif self.mode == 'flanger':
                delay_s = 0.001 + 0.010 * lfo * self.depth
            elif self.mode == 'phaser':
                delay_s = 0.0
            else:
                delay_s = 0.01

            if self.mode == 'phaser':
                w0 = 2 * np.pi * (200 + 4000 * lfo * self.depth) / self.sr
                alpha = np.sin(w0) / (2 * 0.5)
                b0 = 1 - alpha
                b1 = -2 * np.cos(w0)
                b2 = 1 + alpha
                a0 = 1 + alpha
                a1 = -2 * np.cos(w0)
                a2 = 1 - alpha

                b0 /= a0; b1 /= a0; b2 /= a0
                a1_adj = a1 / a0; a2_adj = a2 / a0

                wet = b0 * x + b1 * self._x1 + b2 * self._x2 - a1_adj * self._y1 - a2_adj * self._y2
                self._x2, self._x1 = self._x1, x
                self._y2, self._y1 = self._y1, wet
            else:
                delay_samples = int(delay_s * self.sr)
                read_idx = (self._write_idx - delay_samples) % self._buf_len
                wet = self._buffer[read_idx]
                wet += self.feedback * self._buffer[(read_idx - 1) % self._buf_len]

            out[i] = x * (1 - self.mix) + wet * self.mix
            self._write_idx = (self._write_idx + 1) % self._buf_len
            self._phase += 1.0 / self.sr

        buffer[:] = out

    def update(self):
        pass

    def reset(self):
        self._phase = 0.0
        self._write_idx = 0
        self._buffer.fill(0)
        self._x1 = self._x2 = self._y1 = self._y2 = 0.0

    @staticmethod
    def params():
        return {
            'mode': {'options': ['chorus', 'flanger', 'phaser'], 'default': 'chorus', 'label': 'Mode', 'show_readout': False},
            'rate_hz': {'min': 0.05, 'max': 10, 'default': 0.5, 'label': 'Rate', 'unit': 'Hz', 'show_readout': True},
            'depth': {'min': 0.0, 'max': 1.0, 'default': 0.5, 'label': 'Depth', 'show_readout': True},
            'feedback': {'min': 0.0, 'max': 0.95, 'default': 0.0, 'label': 'Feedback', 'show_readout': True, 'range_dots': True},
            'mix': {'min': 0.0, 'max': 1.0, 'default': 0.5, 'label': 'Mix', 'show_readout': True},
        }
