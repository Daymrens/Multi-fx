import numpy as np


EFFECT_REGISTRY = {}


def register(name, cls):
    EFFECT_REGISTRY[name] = cls


def get_effect_names():
    return list(EFFECT_REGISTRY.keys())


def create_effect(name, sr=44100):
    cls = EFFECT_REGISTRY.get(name)
    if cls:
        return cls(sr)
    return None


class EffectChain:
    def __init__(self, sr=44100):
        self.sr = sr
        self.effects = []

    def add(self, name, position=None):
        effect = create_effect(name, self.sr)
        if effect:
            if position is None:
                self.effects.append(effect)
            else:
                self.effects.insert(position, effect)
        return effect

    def remove(self, index):
        if 0 <= index < len(self.effects):
            self.effects.pop(index)

    def move(self, from_idx, to_idx):
        if 0 <= from_idx < len(self.effects) and 0 <= to_idx < len(self.effects):
            effect = self.effects.pop(from_idx)
            self.effects.insert(to_idx, effect)

    def process(self, buffer):
        for effect in self.effects:
            effect.process(buffer)

    def reset(self):
        for effect in self.effects:
            effect.reset()

    def set_sample_rate(self, sr):
        self.sr = sr
        for effect in self.effects:
            effect.sr = sr
            effect.reset()
            effect.update()

    def to_dict(self):
        data = []
        for effect in self.effects:
            name = type(effect).__name__
            params = {}
            for key, info in effect.params().items():
                params[key] = getattr(effect, key)
            data.append({'name': name, 'bypass': effect.bypass, 'params': params})
        return data

    def from_dict(self, data):
        self.effects = []
        for item in data:
            effect = create_effect(item['name'], self.sr)
            if effect:
                for key, value in item['params'].items():
                    setattr(effect, key, value)
                effect.bypass = item.get('bypass', False)
                effect.update()
                self.effects.append(effect)
