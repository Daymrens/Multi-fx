# Multi-FX

Real-time multi-effects audio processor with a standalone Python app and VST3 plugin.

## Features

- 8 DSP modules: Gate, Filter/EQ, Compressor, Distortion, Chorus/Flanger, Delay, Reverb, Limiter
- Real-time audio processing via sounddevice (standalone)
- VST3 plugin built with JUCE
- Dark OLED theme with green accent
- 5 factory presets

## Quick Start (Standalone)

```bash
pip install -r requirements.txt
python main.py
```

Select your audio interface from the dropdown and hit **Start**.

## DSP Chain

Gate → FilterEQ → Compressor → Distortion → Modulation → Delay → Reverb → Limiter

Each effect can be bypassed, reordered, removed, or added via the chain strip.

## Presets

Load factory presets (Clean Vocal, Guitar Crunch, Ambient Pad, Radio, Drum Smash) from the dropdown, or save your own.

## VST3

The VST3 plugin is located in `build/MultiFX_artefacts/Release/VST3/`. Copy the `.vst3` folder to your system VST3 folder or `%APPDATA%\VST3\`.

## Tech Stack

- **Python**: PyQt6, sounddevice, numpy
- **VST3**: JUCE 8, C++17, CMake
- **Build**: Visual Studio 2022 Build Tools

## Project Structure

```
multi-fx/
├── main.py              # Entry point
├── audio_engine.py      # Audio I/O via sounddevice
├── dsp/                 # Python DSP modules
│   ├── gate.py
│   ├── filter.py
│   ├── compressor.py
│   ├── distortion.py
│   ├── modulation.py
│   ├── delay.py
│   ├── reverb.py
│   └── limiter.py
├── ui/                  # PyQt6 UI components
│   ├── main_window.py
│   ├── chain_view.py
│   ├── effect_panel.py
│   ├── knob.py
│   ├── meter.py
│   └── theme.py
├── presets/             # Factory and user presets
└── pedal/               # UI design references
```
