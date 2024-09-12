from __future__ import annotations

import logging
from abc import ABC, abstractproperty
from collections.abc import Iterable
from pathlib import Path

from dynamicprompts.sampling_context import SamplingContext
from dynamicprompts.enums import SamplingMethod
from dynamicprompts.wildcards import WildcardManager

logger = logging.getLogger(__name__)


class DPAbstractSamplerNode(ABC):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "dynamicPrompts": False}),
                "seed": ("INT", {"default": 0, "display": "number"}),
                "mode": (["random", "combinatorial"], {"default": "random"}),
            },
        }

    @classmethod
    def IS_CHANGED(cls, text: str, seed: int, mode: str):
        # Force re-evaluation of the node
        return float("NaN")

    RETURN_TYPES = ("STRING",)
    FUNCTION = "get_prompt"
    CATEGORY = "Dynamic Prompts"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._initialise_wildcard_manager()
        self._current_mode = ""

    def _initialise_wildcard_manager(self):
        """
        Initialise the wildcard manager.
        """
        wildcards_folder = self._find_wildcards_folder()
        self._wildcard_manager = WildcardManager(path=wildcards_folder)
        self._wildcard_manager._sort_wildcards = False
        self._wildcard_manager.clear_cache()
        self._current_prompt = None

    def _find_wildcards_folder(self) -> Path | None:
        """
        Find the wildcards folder.
        First look in the comfy_dynamicprompts folder, then in the custom_nodes folder, then in the Comfui base folder.
        """
        from folder_paths import base_path, folder_names_and_paths

        wildcard_path = Path(base_path) / "wildcards"

        if wildcard_path.exists():
            return wildcard_path

        extension_path = (
            Path(folder_names_and_paths["custom_nodes"][0][0])
            / "comfyui-dynamicprompts"
        )
        wildcard_path = extension_path / "wildcards"
        wildcard_path.mkdir(parents=True, exist_ok=True)

        return wildcard_path

    def _get_next_prompt(self, prompts: Iterable[str], current_prompt: str, mode:str) -> str:
        """
        Get the next prompt from the prompts generator.
        """
        try:
            return next(prompts)
        except (StopIteration, RuntimeError):
            self._prompts = self.context(mode).sample_prompts(current_prompt)
            try:
                return next(self._prompts)
            except StopIteration:
                logger.exception("No more prompts to generate!")
                return ""

    def has_prompt_changed(self, text: str) -> bool:
        """
        Check if the prompt has changed.
        """
        return self._current_prompt != text

    def context(self, mode: str) -> SamplingContext:
        if mode == "random":
            return SamplingContext(
                wildcard_manager=self._wildcard_manager,
                default_sampling_method=SamplingMethod.RANDOM,
            )
        elif mode == "combinatorial":
            return SamplingContext(
                wildcard_manager=self._wildcard_manager,
                default_sampling_method=SamplingMethod.COMBINATORIAL,
            )   

    def get_prompt(self, text: str, seed: int, mode: str) -> tuple[str]:
        """
        Main entrypoint for this node.
        Using the sampling context, generate a new prompt.
        """

        if self._current_mode != mode:
            self._current_mode = mode
            self._initialise_wildcard_manager()

        if seed > 0:
            self.context(mode).rand.seed(seed)

        if text.strip() == "":
            return ("",)

        if self.has_prompt_changed(text):
            self._current_prompt = text
            self._prompts = self.context(mode).sample_prompts(self._current_prompt)

        if self._prompts is None:
            logger.exception("Something went wrong. Prompts is None!")
            return ("",)

        if self._current_prompt is None:
            logger.exception("Something went wrong. Current prompt is None!")
            return ("",)

        new_prompt = self._get_next_prompt(self._prompts, self._current_prompt, mode)
        print(f"New prompt: {new_prompt}")

        return (str(new_prompt),)