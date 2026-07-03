import sounddevice as sd
import numpy as np


class AudioEngine:
    def __init__(self, chain=None):
        self.chain = chain
        self.sr = 44100
        self._blocksize = 128
        self.input_device = None
        self.output_device = None
        self.routing = 'direct'
        self.direct_monitor = False
        self._stream = None
        self._running = False
        self._peak_in = 0.0
        self._peak_out = 0.0
        self._callback_count = 0
        self._input_latency = 0.0
        self._output_latency = 0.0

    @property
    def blocksize(self):
        return self._blocksize

    @blocksize.setter
    def blocksize(self, value):
        if value == self._blocksize:
            return
        self._blocksize = value
        if self._running:
            self.restart()

    def restart(self):
        was_running = self._running
        if was_running:
            self.stop()
        self._running = False
        if was_running:
            try:
                self.start()
            except RuntimeError:
                pass

    def get_devices(self):
        devices = sd.query_devices()
        hostapis = sd.query_hostapis()
        result = []
        for i, dev in enumerate(devices):
            ha = hostapis[dev['hostapi']]
            result.append({
                'id': i,
                'name': dev['name'],
                'hostapi': ha['name'],
                'inputs': dev['max_input_channels'],
                'outputs': dev['max_output_channels'],
                'sr': dev['default_samplerate'],
                'default_low_in': dev.get('default_low_input_latency', 0),
                'default_low_out': dev.get('default_low_output_latency', 0),
            })
        return result

    def start(self):
        if self._running:
            return
        try:
            self._stream = sd.Stream(
                device=(self.input_device, self.output_device),
                samplerate=self.sr,
                blocksize=self._blocksize,
                dtype='float32',
                channels=max(1, 2),
                callback=self._callback,
                latency='low',
            )
            self._input_latency = self._stream.latency[0] * 1000 if self._stream.latency else 0
            self._output_latency = self._stream.latency[1] * 1000 if self._stream.latency else 0
            self._stream.start()
            self._running = True
        except Exception as e:
            raise RuntimeError(f"Failed to start audio: {e}")

    def stop(self):
        if self._stream:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
            self._stream = None
        self._running = False

    def _callback(self, indata, outdata, frames, time, status):
        if status:
            return
        in_ch = indata.shape[1]
        out_ch = outdata.shape[1]

        mono = np.mean(indata, axis=1) if in_ch >= 1 else np.zeros(frames)

        self._peak_in = float(np.max(np.abs(mono)))

        if self.direct_monitor:
            pass
        elif self.chain:
            self.chain.process(mono)

        self._peak_out = float(np.max(np.abs(mono)))

        for c in range(out_ch):
            outdata[:, c] = mono

        self._callback_count += 1

    @property
    def is_running(self):
        return self._running

    @property
    def peak_in(self):
        return self._peak_in

    @property
    def peak_out(self):
        return self._peak_out

    @property
    def latency_ms(self):
        rt = self._input_latency + self._output_latency
        return rt if rt > 0 else self._blocksize / self.sr * 1000

    @property
    def buffer_ms(self):
        return self._blocksize / self.sr * 1000
