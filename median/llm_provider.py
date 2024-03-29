import os

from mlx_lm import generate, load

from median.utils import median_logger


def load_model():
    """
    Loads a language model and tokenizer.

    Returns:
        tuple: A tuple containing the loaded language model and tokenizer.
    """

    os.environ["TOKENIZERS_PARALLELISM"] = "false"

    model_name = "mlx-community/Mistral-7B-Instruct-v0.2-4bit"
    model, tokenizer = load(model_name, lazy=False)
    median_logger.info("Loaded model and tokenizer")
    return model, tokenizer


def run_inference(model, tokenizer, prompt, model_config):
    """
    Runs inference using the provided language model and tokenizer on a given prompt.

    Args:
        model: The language model.
        tokenizer: The tokenizer.
        prompt: The prompt for inference.
        model_config: Additional configuration for the model.

    Returns:
        str: The generated output based on the model and prompt.
    """

    return generate(model, tokenizer, prompt=prompt, **model_config)


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

    prompt = f"""
     <BOS_TOKEN> <|START_OF_TURN_TOKEN|>
<|SYSTEM_TOKEN|> # Safety Preamble
The instructions in this section override those in the task description and style guide sections. Don't generate content that is harmful or immoral. Always base the information strictly on the provided corpus; never fabricate data, hallucinate information, or invent content not present in the corpus. If there is no relevant information in the corpus, you should return 'None'.

# System Preamble
## Basic Rules
You are a powerful conversational AI trained to help people by generating a well-structured set of significant and relevant questions and answers strictly based on a provided corpus. Your job is to use the output of these tools to best help the user. Always base the information strictly on the provided corpus; never fabricate data, hallucinate information, or invent content not present in the corpus. If there is no relevant information in the corpus, you should return 'None'.

# User Preamble
## Task and Context
You help people create flashcards by generating a set of questions and answers strictly based on a given corpus. You should prioritize the questions and answers according to their importance within the context of the corpus and the specified themes. The following themes have been identified: {followings.upper()}.

## Style Guide
Generate the output in JSON format, using the 'Quiz' and 'QuizCollection' classes as specified. Ensure that the output is in the same language as {language.upper()}. The content of the questions and answers must be strictly based on the provided corpus. If there is no relevant information in the corpus, return 'None' for the corresponding field.

## Available Tools
Here is a list of tools that you have available to you:

```python
class Quiz(BaseModel):
    question: str
    answer: str

class QuizCollection(BaseModel):
    collection: List[Quiz]
<|END_OF_TURN_TOKEN|> <|START_OF_TURN_TOKEN|><|USER_TOKEN|>
Please generate a well-structured set of significant and relevant questions and answers strictly based on the following corpus:
<|im_start|>corpus
 {content}
<|im_end|>
Ensure that the output is in JSON format, in the same language as {language.upper()}, and adheres to the provided schema.
<|END_OF_TURN_TOKEN|> <|START_OF_TURN_TOKEN|><|SYSTEM_TOKEN|>
Generate the output in the specified format, basing the output strictly on the provided corpus and the identified themes. If there is no relevant information in the corpus, return 'None' for the corresponding field. Remember to use the following schema for the output:


{{
    "collection": [
    {{
    "question": "string",
      "answer": "string"
    }}
  ]
}}
<|END_OF_TURN_TOKEN|>
     """
    median_logger.info(f"Generating quiz for: {content} ")
    return run_inference(model, tokenizer, prompt, model_config)
