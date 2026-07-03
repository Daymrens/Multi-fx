import numpy as np


class Reverb:
    def __init__(self, sr=44100):
        self.sr = sr
        self.size = 0.5
        self.damping = 0.5
        self.width = 0.5
        self.predelay_ms = 20.0
        self.dry_wet = 0.3
        self.bypass = False

        self._sr = sr
        self._comb_tunings = [0.0297, 0.0371, 0.0411, 0.0437, 0.0483, 0.0543, 0.0579, 0.0649]
        self._allpass_tunings = [0.005, 0.0017, 0.0037, 0.0047]
        self._num_combs = len(self._comb_tunings)
        self._num_allpasses = len(self._allpass_tunings)
        self._scale = 0.5

        self._comb_delays = [int(t * sr) for t in self._comb_tunings]
        self._allpass_delays = [int(t * sr) for t in self._allpass_tunings]

        self._comb_buffers = [np.zeros(d) for d in self._comb_delays]
        self._allpass_buffers = [np.zeros(d) for d in self._allpass_delays]
        self._comb_indices = [0] * self._num_combs
        self._allpass_indices = [0] * self._num_allpasses
        self._comb_filters = [0.0] * self._num_combs

        self._predelay_buf = np.zeros(int(self.predelay_ms * sr / 1000 + 1))
        self._predelay_idx = 0

    def process(self, buffer):
        if self.bypass:
            return
        damp = self.damping * 0.5
        feedback = self.size * 0.8 + 0.2
        stereo_width = self.width
        mix = self.dry_wet

        n = len(buffer)
        for i in range(n):
            x = buffer[i]

            predelay_n = len(self._predelay_buf)
            if predelay_n > 0:
                delayed = self._predelay_buf[self._predelay_idx]
                self._predelay_buf[self._predelay_idx] = x
                self._predelay_idx = (self._predelay_idx + 1) % predelay_n
            else:
                delayed = x

            left = 0.0
            right = 0.0

            for j in range(self._num_combs):
                buf = self._comb_buffers[j]
                idx = self._comb_indices[j]
                out = buf[idx]
                self._comb_filters[j] = out * (1 - damp) + self._comb_filters[j] * damp
                buf[idx] = delayed + self._comb_filters[j] * feedback
                self._comb_indices[j] = (idx + 1) % len(buf)
                spread = 1.0 + (j % 3 - 1) * 0.2 * stereo_width
                left += out * (1.0 if j < self._num_combs // 2 else 0.0) * spread
                right += out * (0.0 if j < self._num_combs // 2 else 1.0) * spread

            for j in range(self._num_allpasses):
                buf = self._allpass_buffers[j]
                idx = self._allpass_indices[j]
                out = buf[idx]
                buf[idx] = left + out * 0.5
                left = out - left * 0.5
                self._allpass_indices[j] = (idx + 1) % len(buf)

            for j in range(self._num_allpasses):
                buf = self._allpass_buffers[j]
                idx = self._allpass_indices[j]
                out = buf[idx]
                buf[idx] = right + out * 0.5
                right = out - right * 0.5
                self._allpass_indices[j] = (idx + 1) % len(buf)

            buffer[i] = x * (1 - mix) + (left + right) * mix * self._scale

    def update(self):
        pass

    def reset(self):
        for buf in self._comb_buffers:
            buf.fill(0)
        for buf in self._allpass_buffers:
            buf.fill(0)
        self._comb_indices = [0] * self._num_combs
        self._allpass_indices = [0] * self._num_allpasses
        self._comb_filters = [0.0] * self._num_combs
        self._predelay_buf.fill(0)
        self._predelay_idx = 0

    @staticmethod
    def params():
        return {
            'size': {'min': 0.0, 'max': 1.0, 'default': 0.5, 'label': 'Size', 'show_readout': True},
            'damping': {'min': 0.0, 'max': 1.0, 'default': 0.5, 'label': 'Damping', 'show_readout': True},
            'width': {'min': 0.0, 'max': 1.0, 'default': 0.5, 'label': 'Width', 'show_readout': True},
            'predelay_ms': {'min': 0, 'max': 200, 'default': 20, 'label': 'PreDelay', 'unit': 'ms', 'show_readout': True},
            'dry_wet': {'min': 0.0, 'max': 1.0, 'default': 0.3, 'label': 'Mix', 'show_readout': True},
        }
