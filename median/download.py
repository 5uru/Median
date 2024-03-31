import spacy.cli
from mlx_lm import load


model_name = "mlx-community/Mistral-7B-Instruct-v0.2-4bit"
load(model_name, lazy=False)


spacy.cli.download("en_core_web_sm")
