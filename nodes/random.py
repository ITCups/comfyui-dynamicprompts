from functools import lru_cache

from dynamicprompts.enums import SamplingMethod
from dynamicprompts.sampling_context import SamplingContext

from .sampler import DPAbstractSamplerNode


class DPRandomGenerator(DPAbstractSamplerNode):
    pass