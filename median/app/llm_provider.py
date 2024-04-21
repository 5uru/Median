import os

from mlx_lm import generate , load

from median.app.utils import median_logger


def load_model( ) :
    """
    Loads a language model and tokenizer.

    Returns:
        tuple: A tuple containing the loaded language model and tokenizer.
    """

    os.environ[ "TOKENIZERS_PARALLELISM" ] = "false"

    model_name = "mlx-community/Meta-Llama-3-8B-Instruct-4bit"
    model , tokenizer = load(model_name , lazy=False)
    median_logger.info("Loaded model and tokenizer")
    return model , tokenizer


def run_inference(model , tokenizer , prompt , model_config) :
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

    return generate(model , tokenizer , prompt=prompt , **model_config)


def generation(content: str , language: str , followings: str) :
    """
    Generates a quiz based on the provided content, language, and specified themes.

    Args:
        content (str): The content for which the quiz is generated.
        language (str): The language for the quiz.
        followings (str): The identified themes for the quiz.

    Returns:
        str: The generated quiz output.
    """

    model , tokenizer = load_model( )

    model_config = {
            "verbose" : True ,
            "temp" : 0.7 ,
            "max_tokens" : 4000 ,
            "repetition_penalty" : 1.1 ,
    }

    prompt = f"""
<|begin_of_text|><|start_header_id|>system<|end_header_id|>

# Safety Preamble The instructions in this section override those in the task description and style guide sections. Do not generate content that is harmful or immoral. Always strictly base the 
 information on the provided corpus; never fabricate data, hallucinate information, or invent content not present in the corpus. If there is no relevant information in the corpus, 
  you must return 'None'.

# System Preamble ## Basic Rules You are a conversational AI designed to help users by generating a structured set of significant and relevant questions and answers strictly based on a provided 
 corpus. You must never fabricate data, hallucinate information, or create content not found in the corpus. If the corpus does not contain relevant information, return 'None'.

# User Preamble ## Task and Context You assist users in creating flashcards by generating a set of questions and answers strictly based on a given corpus. Prioritize the questions and answers 
 according to their importance within the context of the corpus and the specified themes. Use the themes identified: {followings.upper( )}.

## Style Guide
Generate output in JSON format using the 'Quiz' and 'QuizCollection' classes as specified. Ensure the output is in the same language as {language.upper( )}. The content of the questions and answers 
 must be strictly based on the provided corpus. If there is no relevant information in the corpus, return 'None' for the corresponding field.

## Available Tools
Here is a list of tools available to you:
```python
class Quiz(BaseModel):
    question: str
    answer: str

class QuizCollection(BaseModel):
    collection: List[Quiz]
```

## Instructions for Use
Please generate a structured set of significant and relevant questions and answers based on the following corpus:

{content}

Ensure that the output is in JSON format, in the same language as {language.upper( )}, and adheres to the provided schema. If there is no relevant information in the corpus, return 'None' for the 
 corresponding field. Remember to use the following schema for the output:

{{
    "collection": [
        {{
    "question": "string",
            "answer": "string"
        }}
    ]
}}
 <|eot_id|><|start_header_id|>assistant<|end_header_id|>
     """
    median_logger.info(f"Generating quiz for: {content} ")
    return run_inference(model , tokenizer , prompt , model_config)
