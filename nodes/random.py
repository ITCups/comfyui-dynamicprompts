from functools import lru_cache

from dynamicprompts.enums import SamplingMethod
from dynamicprompts.sampling_context import SamplingContext

from .sampler import DPAbstractSamplerNode, DPAbstractSamplerNodeAdvanced

class DPRandomGeneratorAdvanced(DPAbstractSamplerNodeAdvanced):
    pass

class DPRandomGenerator(DPAbstractSamplerNode):
    pass
