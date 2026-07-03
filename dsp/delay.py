import numpy as np


class Delay:
    def __init__(self, sr=44100):
        self.sr = sr
        self.time_ms = 300.0
        self.feedback = 0.3
        self.lp_cutoff = 8000.0
        self.mix = 0.3
        self.ping_pong = False
        self.bypass = False

        self._max_delay = int(sr * 2)
        self._buffer = np.zeros(self._max_delay)
        self._write_idx = 0
        self._lp_state = 0.0

    def process(self, buffer):
        if self.bypass:
            return
        n = len(buffer)
        delay_samples = min(int(self.time_ms * self.sr / 1000), self._max_delay - 1)
        rc = 1.0 / (2 * np.pi * max(self.lp_cutoff, 20))
        dt = 1.0 / self.sr
        alpha = dt / (rc + dt)

        for i in range(n):
            x = buffer[i]
            read_idx = (self._write_idx - delay_samples) % self._max_delay
            wet = self._buffer[read_idx]

            self._lp_state += alpha * (wet - self._lp_state)
            wet_filtered = self._lp_state

            self._buffer[self._write_idx] = x + wet_filtered * self.feedback

            if self.ping_pong:
                read_idx2 = (self._write_idx - delay_samples * 2) % self._max_delay
                wet2 = self._buffer[read_idx2]
                buffer[i] = x * (1 - self.mix) + wet * self.mix * 0.7 + wet2 * self.mix * 0.3
            else:
                buffer[i] = x * (1 - self.mix) + wet * self.mix

            self._write_idx = (self._write_idx + 1) % self._max_delay

    def update(self):
        pass

    def reset(self):
        self._buffer.fill(0)
        self._write_idx = 0
        self._lp_state = 0.0

    @staticmethod
    def params():
        return {
            'time_ms': {'min': 10, 'max': 2000, 'default': 300, 'label': 'Time', 'unit': 'ms', 'show_readout': True},
            'feedback': {'min': 0.0, 'max': 0.95, 'default': 0.3, 'label': 'Feedback', 'show_readout': True, 'range_dots': True},
            'lp_cutoff': {'min': 200, 'max': 20000, 'default': 8000, 'label': 'LP Cut', 'unit': 'Hz', 'show_readout': True},
            'mix': {'min': 0.0, 'max': 1.0, 'default': 0.3, 'label': 'Mix', 'show_readout': True},
            'ping_pong': {'options': [True, False], 'default': False, 'label': 'PingPong', 'show_readout': False},
        }
