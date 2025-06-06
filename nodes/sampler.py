from __future__ import annotations

import logging
from abc import ABC, abstractproperty
from collections.abc import Iterable
from pathlib import Path
from hashlib import sha256

from dynamicprompts.sampling_context import SamplingContext
from dynamicprompts.enums import SamplingMethod
from dynamicprompts.wildcards import WildcardManager

logger = logging.getLogger(__name__)

class DPAbstractSamplerNodeAdvanced(ABC):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "dynamicPrompts": False}),
                "seed": ("INT", {"default": 0, "display": "number"}),
                "sampling_mode": (["random", "combinatorial"], {"default": "random"}),
                "refresh_mode": (["always", "on_value_change"], {"default": "on_value_change"}),
                "console_output": (["off", "new_prompt", "debug"], {"default": "off"})
            },
        }

    @classmethod
    def IS_CHANGED(cls, text: str, seed: int, sampling_mode: str, refresh_mode: str, console_output: str):
        if refresh_mode == "always":
            # Force re-evaluation of the node, (original default behavior)
            return float("NaN")
        else:
            # Re-evaluate only in case of change in the input values
            m = sha256()
            m.update(str(seed).encode())
            m.update(sampling_mode.encode())
            m.update(refresh_mode.encode())
            m.update(console_output.encode())
            m.update("".encode() if text is None else text.encode())
            if (console_output == "debug"):
                truncated_text = (text[:50] + '...') if len(text) > 50 else text
                print(f"DPAbstractSamplerNode.IS_CHANGED: hash={m.hexdigest()} <- {{seed={str(seed)}, sampling_mode={sampling_mode}, refresh_mode={refresh_mode}, console_output={console_output}, text (truncated): \"{truncated_text}\"}}")
            return m.hexdigest()

    RETURN_TYPES = ("STRING",)
    FUNCTION = "get_prompt"
    CATEGORY = "Dynamic Prompts"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._initialise_wildcard_manager()
        self._sampling_mode = ""

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
            / "comfyui-dynamicprompts-batch"
        )
        wildcard_path = extension_path / "wildcards"
        wildcard_path.mkdir(parents=True, exist_ok=True)

        return wildcard_path

    def _get_next_prompt(self, prompts: Iterable[str], current_prompt: str, sampling_mode:str) -> str:
        """
        Get the next prompt from the prompts generator.
        """
        try:
            return next(prompts)
        except (StopIteration, RuntimeError):
            self._prompts = self.context(sampling_mode).sample_prompts(current_prompt)
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

    def context(self, sampling_mode: str) -> SamplingContext:
        if sampling_mode == "random":
            return SamplingContext(
                wildcard_manager=self._wildcard_manager,
                default_sampling_method=SamplingMethod.RANDOM,
            )
        elif sampling_mode == "combinatorial":
            return SamplingContext(
                wildcard_manager=self._wildcard_manager,
                default_sampling_method=SamplingMethod.COMBINATORIAL,
            )

    def get_prompt(self, text: str, seed: int, sampling_mode: str, refresh_mode: str, console_output: str) -> tuple[str]:
        """
        Main entrypoint for this node.
        Using the sampling context, generate a new prompt.
        """

        if self._sampling_mode != sampling_mode:
            self._sampling_mode = sampling_mode
            self._initialise_wildcard_manager()

        if seed > 0:
            self.context(sampling_mode).rand.seed(seed)

        if text.strip() == "":
            return ("",)

        if self.has_prompt_changed(text):
            self._current_prompt = text
            self._prompts = self.context(sampling_mode).sample_prompts(self._current_prompt)

        if self._prompts is None:
            logger.exception("Something went wrong. Prompts is None!")
            return ("",)

        if self._current_prompt is None:
            logger.exception("Something went wrong. Current prompt is None!")
            return ("",)

        new_prompt = self._get_next_prompt(self._prompts, self._current_prompt, sampling_mode)
        if (console_output != "off"):
            print(f"New prompt: {new_prompt}")

        return (str(new_prompt),)

class DPAbstractSamplerNode(DPAbstractSamplerNodeAdvanced):
    DEFAULT_SAMPLING_MODE = "random"
    DEFAULT_REFRESH_MODE = "on_value_change"
    DEFAULT_CONSOLE_OUTPUT = "off"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "dynamicPrompts": False}),
                "seed": ("INT", {"default": 0, "display": "number"})
            },
        }

    @classmethod
    def IS_CHANGED(cls, text: str, seed: int):
        return super().IS_CHANGED(text, seed, sampling_mode=cls.DEFAULT_SAMPLING_MODE, refresh_mode=cls.DEFAULT_REFRESH_MODE, console_output=cls.DEFAULT_CONSOLE_OUTPUT)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_prompt(self, text: str, seed: int) -> tuple[str]:
        return super().get_prompt(text, seed, sampling_mode=self.DEFAULT_SAMPLING_MODE, refresh_mode=self.DEFAULT_SAMPLING_MODE, console_output=self.DEFAULT_CONSOLE_OUTPUT)
