from mlx_lm import generate, load

from median.utils import median_logger
import os


def run_inference(prompt):
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    config = {
        "verbose": True,
        "temp": 0.8,
        "max_tokens": 1500,
        "repetition_penalty": 1.1,
    }
    model_name = "jonathansuru/dolphin-2.1-mistral-7b-8bit"
    model, tokenizer = load(model_name, lazy=True)
    median_logger.info("Loaded model and tokenizer")
    return generate(model, tokenizer, prompt=prompt, **config)


def generation(content, language, followings):
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
    return run_inference(prompt)
