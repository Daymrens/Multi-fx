from .gate import Gate
from .filter import FilterEQ
from .compressor import Compressor
from .distortion import Distortion
from .modulation import Modulation
from .delay import Delay
from .reverb import Reverb
from .limiter import Limiter
from .chain import EffectChain, register

register('Gate', Gate)
register('FilterEQ', FilterEQ)
register('Compressor', Compressor)
register('Distortion', Distortion)
register('Modulation', Modulation)
register('Delay', Delay)
register('Reverb', Reverb)
register('Limiter', Limiter)
