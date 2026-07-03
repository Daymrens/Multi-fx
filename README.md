# Multi-FX

Real-time multi-effects audio processor — standalone Python app and VST3 plugin.

Process live instrument audio through an 8-module DSP chain with an intuitive drag-and-drop pedalboard interface.

---

## Specs

### Audio
| Param | Value |
|-------|-------|
| Sample rate | 44100 Hz |
| Block size | 128 samples |
| Latency | ~2.9 ms |
| Bit depth | 32-bit float |
| I/O | sounddevice (ASIO/WASAPI/MME) |
| Channels | Mono in → stereo out (processed mono to both) |

### Routing Modes
| Mode | Behavior |
|------|----------|
| Direct | Processed signal → interface output |
| Loopback | Processed signal → VB-Cable → FL Studio |
| Split | Simultaneous Direct + Loopback |

### DSP Chain (8 modules)

| Module | Parameters | Range |
|--------|-----------|-------|
| **Gate** | Threshold | -80 – 0 dB |
| | Attack | 0.1 – 50 ms |
| | Hold | 0 – 200 ms |
| | Release | 5 – 500 ms |
| **FilterEQ** | Type | LP / HP / BP / Notch / LowShelf / HighShelf / Peak |
| | Frequency | 20 – 20000 Hz |
| | Q | 0.1 – 20 |
| | Gain | -24 – +24 dB |
| **Compressor** | Threshold | -60 – 0 dB |
| | Ratio | 1:1 – 20:1 |
| | Knee | 0 – 12 dB |
| | Attack | 0.1 – 100 ms |
| | Release | 5 – 500 ms |
| | Makeup | 0 – 24 dB |
| **Distortion** | Type | Soft / Hard / Tube / Fuzz |
| | Drive | 0 – 10 |
| | Mix | 0 – 100% |
| | Output | -24 – +24 dB |
| **Modulation** | Mode | Chorus / Flanger / Phaser |
| | Rate | 0.05 – 10 Hz |
| | Depth | 0 – 100% |
| | Feedback | 0 – 95% |
| | Mix | 0 – 100% |
| **Delay** | Time | 10 – 2000 ms |
| | Feedback | 0 – 95% |
| | LP Cutoff | 200 – 20000 Hz |
| | Mix | 0 – 100% |
| | Ping-Pong | On / Off |
| **Reverb** | Size | 0 – 100% |
| | Damping | 0 – 100% |
| | Width | 0 – 100% |
| | Pre-delay | 0 – 200 ms |
| | Mix | 0 – 100% |
| **Limiter** | Ceiling | -24 – 0 dB |
| | Release | 5 – 500 ms |
| | Lookahead | 0 – 10 ms |

### Presets

5 factory presets included (auto-generated on first run):

| Preset | Chain |
|--------|-------|
| Clean Vocal | Gate → HPF → Compressor → Reverb → Limiter |
| Guitar Crunch | Gate → LPF → Distortion → Compressor → Delay → Limiter |
| Ambient Pad | LPF → Chorus → Ping-Pong Delay → Reverb → Limiter |
| Radio | Gate → BPF → Distortion → Compressor → Limiter |
| Drum Smash | Gate → Compressor → Distortion → Peak EQ → Limiter |

---

## Quick Start (Standalone)

```bash
pip install -r requirements.txt
python main.py
```

1. Select your audio interface from the Input/Output dropdowns
2. Click **Start**
3. Adjust effect parameters or load a preset

## VST3 Plugin

Location: `build/MultiFX_artefacts/Release/VST3/MultiFX.vst3` (3.7 MB)

Copy to your VST3 search path:
```
%APPDATA%\VST3\     (user, no admin needed)
C:\Program Files\Common Files\VST3\     (system-wide, admin)
```

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| GUI | PyQt6 |
| Audio I/O | sounddevice + numpy |
| DSP | Python (standalone), C++17 JUCE (VST3) |
| VST3 Framework | JUCE 8 |
| Compiler | MSVC 19.44, C++17 |
| Build | CMake 4.3.4 |
| Platform | Windows 11 x64 |

### Requirements
- Python 3.13+
- Visual Studio 2022 Build Tools (VST3 only)
- Audio interface with ASIO drivers recommended

---

## Project Structure

```
multi-fx/
├── main.py                 # Application entry point
├── audio_engine.py         # Audio I/O via sounddevice
├── preset_manager.py       # JSON preset save/load
├── requirements.txt
├── dsp/                    # Python DSP engine (1200+ lines)
│   ├── chain.py            # Effect chain & registry
│   ├── gate.py             # Noise gate
│   ├── filter.py           # Biquad filter (7 types)
│   ├── compressor.py       # Compressor with soft knee
│   ├── distortion.py       # 4 distortion algorithms
│   ├── modulation.py       # Chorus / Flanger / Phaser
│   ├── delay.py            # Delay with LP feedback
│   ├── reverb.py           # Schroeder reverb
│   └── limiter.py          # Lookahead limiter
├── ui/                     # PyQt6 interface
│   ├── main_window.py      # Main application window
│   ├── chain_view.py       # Drag-and-drop effect chain
│   ├── effect_panel.py     # Per-effect parameter controls
│   ├── knob.py             # Custom rotary knob widget
│   ├── meter.py            # Peak level meter
│   └── theme.py            # Design system tokens
├── presets/                # Factory & user presets (JSON)
├── pedal/                  # UI design references
└── multi-fx-vst3/          # VST3 C++ source (separate project)
```

---

## Building the VST3 (from source)

```bash
cd multi-fx-vst3
cmake -B build -G "Visual Studio 17 2022"
cmake --build build --config Release
```

Requires JUCE 8 (fetched via CMake FetchContent) and Visual Studio 2022 Build Tools.

---

## License

MIT
