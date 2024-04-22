import os

from mlx_lm import generate, load

from median.app.prompts import prompt
from median.app.utils import median_logger


def load_model():
    """
    Loads a language model and tokenizer.

    Returns:
        tuple: A tuple containing the loaded language model and tokenizer.
    """

    os.environ["TOKENIZERS_PARALLELISM"] = "false"

    model_name = "mlx-community/Meta-Llama-3-8B-Instruct-4bit"
    model, tokenizer = load(model_name, lazy=False)
    median_logger.info("Loaded model and tokenizer")
    return model, tokenizer


def run_inference(model, tokenizer, instruction, model_config):
    """
    Runs inference using the provided language model and tokenizer on a given prompt.

    Args:
        model: The language model.
        tokenizer: The tokenizer.
        instruction: The instruction for inference.
        model_config: Additional configuration for the model.

    Returns:
        str: The generated output based on the model and prompt.
    """

    return generate(model, tokenizer, prompt=instruction, **model_config)


def generation(content: str, language: str, followings: str):
    """
    Generates a quiz based on the provided content, language, and specified themes.

    Args:
        content (str): The content for which the quiz is generated.
        language (str): The language for the quiz.
        followings (str): The identified themes for the quiz.

    Returns:
        str: The generated quiz output.
    """

    model, tokenizer = load_model()

    model_config = {
        "verbose": True,
        "temp": 0.7,
        "max_tokens": 4000,
        "repetition_penalty": 1.1,
    }

    instruction = prompt.format(
        followings=followings.upper(), language=language.upper(), content=content
    )
    median_logger.info(f"Generating quiz for: {content} ")
    return run_inference(model, tokenizer, instruction, model_config)
