from __future__ import annotations

import logging
from abc import ABC, abstractproperty
from collections.abc import Iterable
from pathlib import Path
from .sampler import DPAbstractSamplerNode
import torch
import comfy.model_management

from dynamicprompts.sampling_context import SamplingContext
from dynamicprompts.wildcards import WildcardManager



MAX_RESOLUTION=16384

logger = logging.getLogger(__name__)

class DPAbstractSamplerBatchNode(DPAbstractSamplerNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "dynamicPrompts": False}),
                "seed": ("INT", {"default": 0, "display": "number"}),
                "autorefresh": (["Yes", "No"], {"default": "No"}),
                "width": ("INT", {"default": 512, "min": 16, "max": MAX_RESOLUTION, "step": 8, "tooltip": "The width of the latent images in pixels."}),
                "height": ("INT", {"default": 512, "min": 16, "max": MAX_RESOLUTION, "step": 8, "tooltip": "The height of the latent images in pixels."}),
                "clip": ("CLIP", {"tooltip": "The CLIP model used for encoding the text."}),
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 4096, "tooltip": "The number of latent images in the batch."}),
            },
        }

    @classmethod
    def IS_CHANGED(cls, text: str, seed: int, autorefresh: str, width, height,clip, batch_size):
        # Force re-evaluation of the node
        return float("NaN")

    RETURN_TYPES = ("STRING","CONDITIONING","LATENT")
    FUNCTION = "get_batch_prompts"
    CATEGORY = "Dynamic Prompts"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.device = comfy.model_management.intermediate_device()

    #def encode(self, clip, text):
    #   tokens = clip.tokenize(text)
    #    output = clip.encode_from_tokens(tokens, return_pooled=True, return_dict=True)
    #    cond = output.pop("cond")
    #    return ([cond, output])

    """
        interpolated_conditioning = addWeighted([[cond_to, {"pooled_output": pooled_to}]],
                                                [[cond_from, {"pooled_output": pooled_from}]],
                                                weight_series[i],max_size)

        interpolated_cond = interpolated_conditioning[0][0]
        interpolated_pooled = interpolated_conditioning[0][1].get("pooled_output", pooled_from)

        cond_out.append(interpolated_cond)
        pooled_out.append(interpolated_pooled)

    final_pooled_output = torch.cat(pooled_out, dim=0)
    final_conditioning = torch.cat(cond_out, dim=0)

    return [[final_conditioning, {"pooled_output": final_pooled_output}]]
    """

    def encode(self, clip, text):
        if isinstance(text, list):
            batched_cond = []
            batched_pooled = []
            
            for single_text in text:
                tokens = clip.tokenize(single_text)
                cond, pooled = clip.encode_from_tokens(tokens, return_pooled=True)
                batched_cond.append(cond)
                batched_pooled.append(pooled)            

            # Stack along a new dimension to create a batched tensor
#            batched_cond_tensor = torch.stack(batched_cond, dim=0).squeeze(1)        
#            return ([[batched_cond_tensor, {"pooled_output": batched_pooled}]])

            final_pooled_output = torch.cat(batched_pooled, dim=0)
            final_conditioning = torch.cat(batched_cond, dim=0)

            return [[final_conditioning, {"pooled_output": final_pooled_output}]]
        else:
            tokens = clip.tokenize(text)
            cond, pooled = clip.encode_from_tokens(tokens, return_pooled=True)
            return ([[cond, {"pooled_output": pooled}]])

    def get_batch_prompts(self, text, seed,autorefresh, width, height, clip, batch_size=1):
        
        conditioning = list()
        prompt = list()
        for i in range(batch_size):
            new_prompt = str(self.get_prompt(text,seed+i,autorefresh)[0])
            prompt.append(new_prompt)
                      
        conditioning = self.encode(clip,prompt)
        latent = torch.zeros([batch_size, 4, height // 8, width // 8], device=self.device)
        return (prompt,conditioning, {"samples":latent},)





    @abstractproperty
    def context(self) -> SamplingContext:
        ...
