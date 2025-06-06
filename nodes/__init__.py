from .combinatorial import DPCombinatorialGenerator
from .feeling_lucky import DPFeelingLucky
from .jinja import DPJinja
from .magicprompt import DPMagicPrompt
from .output_node import OutputString
from .random import DPRandomGenerator, DPRandomGeneratorAdvanced
from .random_batch import DPRandomGeneratorBatch
from .combinatorial_batch import DPCombinatorialGeneratorBatch

NODE_CLASS_MAPPINGS = {
    "DPRandomGeneratorAdvanced": DPRandomGeneratorAdvanced,
    "DPRandomGenerator": DPRandomGenerator,
    "DPCombinatorialGenerator": DPCombinatorialGenerator,
    "DPFeelingLucky": DPFeelingLucky,
    "DPJinja": DPJinja,
    "DPMagicPrompt": DPMagicPrompt,
    "DPOutput": OutputString,
    "DPRandomGeneratorBatch" : DPRandomGeneratorBatch,
    "DPCombinatorialGeneratorBatch": DPCombinatorialGeneratorBatch,
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "DPRandomGeneratorAdvanced": "Random Prompts Advanced",
    "DPRandomGenerator": "Random Prompts",
    "DPCombinatorialGenerator": "Combinatorial Prompts",
    "DPFeelingLucky": "I'm Feeling Lucky",
    "DPJinja": "Jinja2 Templates",
    "DPMagicPrompt": "Magic Prompt",
    "DPOutput": "OutputString",
    "DPRandomGeneratorBatch": "Random Prompts Batch",
    "DPCombinatorialGeneratorBatch": "Combinatorial Prompts Batch"
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
