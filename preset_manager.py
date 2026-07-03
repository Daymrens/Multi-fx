import json
from pathlib import Path

PRESET_DIR = Path(__file__).parent / 'presets'


def save_preset(name, chain_data):
    safe = name.replace(' ', '_').lower()
    path = PRESET_DIR / f"{safe}.json"
    with open(path, 'w') as f:
        json.dump({'name': name, 'chain': chain_data}, f, indent=2)
    return path


def load_preset(path):
    with open(path) as f:
        return json.load(f)


def list_presets():
    if not PRESET_DIR.exists():
        return []
    presets = []
    for f in sorted(PRESET_DIR.glob('*.json')):
        try:
            data = load_preset(f)
            presets.append({'name': data.get('name', f.stem), 'path': str(f)})
        except Exception:
            pass
    return presets


def load_factory_presets(chain):
    for preset in list_presets():
        pass


FACTORY_PRESETS = {
    'clean_vocal': {
        'name': 'Clean Vocal',
        'chain': [
            {'name': 'Gate', 'bypass': False, 'params': {'threshold': -50, 'attack_ms': 0.5, 'hold_ms': 10, 'release_ms': 40}},
            {'name': 'FilterEQ', 'bypass': False, 'params': {'type': 'HP', 'freq': 80, 'q': 0.707, 'gain_db': 0}},
            {'name': 'Compressor', 'bypass': False, 'params': {'threshold': -24, 'ratio': 3.5, 'knee_db': 6, 'attack_ms': 3, 'release_ms': 40, 'makeup_db': 4}},
            {'name': 'Reverb', 'bypass': False, 'params': {'size': 0.4, 'damping': 0.6, 'width': 0.5, 'predelay_ms': 15, 'dry_wet': 0.25}},
            {'name': 'Limiter', 'bypass': False, 'params': {'threshold': -1, 'release_ms': 50, 'lookahead_ms': 2}},
        ]
    },
    'guitar_crunch': {
        'name': 'Guitar Crunch',
        'chain': [
            {'name': 'Gate', 'bypass': False, 'params': {'threshold': -45, 'attack_ms': 0.5, 'hold_ms': 5, 'release_ms': 30}},
            {'name': 'FilterEQ', 'bypass': False, 'params': {'type': 'LP', 'freq': 6000, 'q': 0.707, 'gain_db': 0}},
            {'name': 'Distortion', 'bypass': False, 'params': {'type': 'tube', 'drive': 4.0, 'mix': 0.8, 'output_db': 0}},
            {'name': 'Compressor', 'bypass': False, 'params': {'threshold': -18, 'ratio': 4, 'knee_db': 6, 'attack_ms': 2, 'release_ms': 30, 'makeup_db': 2}},
            {'name': 'Delay', 'bypass': True, 'params': {'time_ms': 400, 'feedback': 0.2, 'lp_cutoff': 5000, 'mix': 0.2, 'ping_pong': False}},
            {'name': 'Limiter', 'bypass': False, 'params': {'threshold': -0.5, 'release_ms': 50, 'lookahead_ms': 2}},
        ]
    },
    'ambient_pad': {
        'name': 'Ambient Pad',
        'chain': [
            {'name': 'FilterEQ', 'bypass': False, 'params': {'type': 'LP', 'freq': 4000, 'q': 0.707, 'gain_db': 0}},
            {'name': 'Modulation', 'bypass': False, 'params': {'mode': 'chorus', 'rate_hz': 0.3, 'depth': 0.7, 'feedback': 0.2, 'mix': 0.5}},
            {'name': 'Delay', 'bypass': False, 'params': {'time_ms': 600, 'feedback': 0.4, 'lp_cutoff': 4000, 'mix': 0.35, 'ping_pong': True}},
            {'name': 'Reverb', 'bypass': False, 'params': {'size': 0.85, 'damping': 0.3, 'width': 0.8, 'predelay_ms': 30, 'dry_wet': 0.5}},
            {'name': 'Limiter', 'bypass': False, 'params': {'threshold': -1, 'release_ms': 50, 'lookahead_ms': 2}},
        ]
    },
    'radio': {
        'name': 'Radio',
        'chain': [
            {'name': 'Gate', 'bypass': False, 'params': {'threshold': -40, 'attack_ms': 0.5, 'hold_ms': 5, 'release_ms': 20}},
            {'name': 'FilterEQ', 'bypass': False, 'params': {'type': 'BP', 'freq': 2000, 'q': 2.0, 'gain_db': 0}},
            {'name': 'Distortion', 'bypass': True, 'params': {'type': 'soft', 'drive': 1.0, 'mix': 0.3, 'output_db': -3}},
            {'name': 'Compressor', 'bypass': False, 'params': {'threshold': -20, 'ratio': 6, 'knee_db': 3, 'attack_ms': 5, 'release_ms': 80, 'makeup_db': 3}},
            {'name': 'Limiter', 'bypass': False, 'params': {'threshold': -0.5, 'release_ms': 50, 'lookahead_ms': 2}},
        ]
    },
    'drum_smash': {
        'name': 'Drum Smash',
        'chain': [
            {'name': 'Gate', 'bypass': False, 'params': {'threshold': -30, 'attack_ms': 0.1, 'hold_ms': 5, 'release_ms': 15}},
            {'name': 'Compressor', 'bypass': False, 'params': {'threshold': -30, 'ratio': 8, 'knee_db': 3, 'attack_ms': 0.5, 'release_ms': 30, 'makeup_db': 6}},
            {'name': 'Distortion', 'bypass': False, 'params': {'type': 'hard', 'drive': 2.0, 'mix': 0.4, 'output_db': -6}},
            {'name': 'FilterEQ', 'bypass': False, 'params': {'type': 'Peak', 'freq': 100, 'q': 1.5, 'gain_db': 4}},
            {'name': 'Limiter', 'bypass': False, 'params': {'threshold': -2, 'release_ms': 30, 'lookahead_ms': 1}},
        ]
    },
}


def init_factory_presets():
    PRESET_DIR.mkdir(parents=True, exist_ok=True)
    for key, data in FACTORY_PRESETS.items():
        path = PRESET_DIR / f"{key}.json"
        if not path.exists():
            with open(path, 'w') as f:
                json.dump(data, f, indent=2)
