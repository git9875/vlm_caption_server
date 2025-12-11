'''
Provides the models within services to the apps to use.
List of available models and services to present to the user.
Instantiate and hold in memory.
Given an image (or media) and prompt, run inference and return results.
'''
from importlib import import_module
from classes import available_service_model

selected_service_model = None


available_service_models = {
    "Qwen3-VLM-8B-Ollama":available_service_model(
        name="Qwen3-VLM-8B-Ollama",
        module_path="services.local_ollama",
        specific_model_name="qwen3-vl:8b",
        description="Qwen3-VLM-8B using local Ollama server."
    ),
    "microsoft/Florence-2-base-ft":available_service_model(
        name="microsoft/Florence-2-base-ft",
        module_path="services.local_florence2",
        specific_model_name="ducviet00/Florence-2-base-hf",
        description="Local ducviet00/Florence-2-base-hf using Huggingface transformers. This is a fork of microsoft/Florence-2-base-ft that is currently working."
    ),
    "MiniCPM-V-2.6-8b-Ollama":available_service_model(
        name="MiniCPM-V 2.6 Ollama",
        module_path="services.local_ollama",
        specific_model_name="minicpm-v:8b",
        description="Mini-CPM-V-2.6 8B using local Ollama server."
    ),
}


available_prompts = {
    "detailed": "Describe the image in detail in one paragraph. Response should be text only without Markdown.",
    "short": "Provide a brief description of the image within 40 words or less.",
    "tags": "Provide a comma delimited list of tags that describe the image in order of relevance.",
}


def start_service(service_model: str):
    global selected_service_model
    if service_model not in available_service_models:
        raise ValueError(f"Service model '{service_model}' not found.")
    
    service_info = available_service_models[service_model]
    service_module = import_module(service_info.module_path)
    model_instance = service_module.model_service(service_info.specific_model_name)
    selected_service_model = model_instance
    selected_service_model.load_model()

def get_caption(image_path: str, prompt: str) -> str:
    if selected_service_model is None:
        raise RuntimeError("No service model has been started.")
    
    caption = selected_service_model.run_inference(image_path, prompt)

    # remove anything after ' (' to clean up captions from some models
    if ' (' in caption:
        caption = caption.split(' (')[0]
    return caption

def get_available_models() -> list:
    return list(available_service_models.keys())

def close_service():
    global selected_service_model
    if selected_service_model is not None:
        selected_service_model.close_model()
        selected_service_model = None

