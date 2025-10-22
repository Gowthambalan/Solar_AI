import yaml
from langchain_ollama import ChatOllama
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.config.constants import PROMPT_PATH, MODEL_NAME

def load_llm_chain():
    """Load LLM and prompt from YAML."""
    with open(PROMPT_PATH, "r") as f:
        prompt_data = yaml.safe_load(f)
    prompt_text = prompt_data["canonical_prompt"]

    llm = ChatOllama(model=MODEL_NAME, temperature=0)
    prompt = PromptTemplate.from_template(prompt_text)
    return prompt | llm | JsonOutputParser()


