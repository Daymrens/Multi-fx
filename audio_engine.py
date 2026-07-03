import sounddevice as sd
import numpy as np


class AudioEngine:
    def __init__(self, chain=None):
        self.chain = chain
        self.sr = 44100
        self.blocksize = 128
        self.input_device = None
        self.output_device = None
        self.routing = 'direct'  # direct, loopback, split
        self._stream = None
        self._running = False
        self._peak_in = 0.0
        self._peak_out = 0.0
        self._callback_count = 0

    def get_devices(self):
        devices = sd.query_devices()
        result = []
        for i, dev in enumerate(devices):
            result.append({
                'id': i,
                'name': dev['name'],
                'inputs': dev['max_input_channels'],
                'outputs': dev['max_output_channels'],
                'sr': dev['default_samplerate'],
            })
        return result

    def find_asio_devices(self):
        devices = sd.query_devices()
        asio_devices = []
        for i, dev in enumerate(devices):
            if 'ASIO' in dev['name'].upper() or 'FL Studio ASIO' in dev['name']:
                asio_devices.append({
                    'id': i,
                    'name': dev['name'],
                    'inputs': dev['max_input_channels'],
                    'outputs': dev['max_output_channels'],
                })
        return asio_devices

    def start(self):
        if self._running:
            return
        try:
            self._stream = sd.Stream(
                device=(self.input_device, self.output_device),
                samplerate=self.sr,
                blocksize=self.blocksize,
                dtype='float32',
                channels=max(1, 2),
                callback=self._callback,
                latency='low',
            )
            self._stream.start()
            self._running = True
        except Exception as e:
            raise RuntimeError(f"Failed to start audio: {e}")

    def stop(self):
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        self._running = False

    def _callback(self, indata, outdata, frames, time, status):
        if status:
            return
        in_ch = indata.shape[1]
        out_ch = outdata.shape[1]

        mono = np.mean(indata, axis=1) if in_ch >= 1 else np.zeros(frames)

        self._peak_in = float(np.max(np.abs(mono)))

        if self.chain:
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
        return self.blocksize / self.sr * 1000

    def update(self):
        pass
