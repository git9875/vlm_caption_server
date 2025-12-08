from ..classes import model_service_abstract
from ollama import chat
from ollama import ChatResponse
import ollama

class model_service(model_service_abstract):
    service = None
    client = ollama.Client()

    def __init__(self, specific_model_name):
        self.specific_model_name = specific_model_name

    def load_model(self):
        service = None
        # nothing to hold into memory with Ollama chat

    def run_inference(self, image_path, prompt):
        # Not async because multiple requests could use too much memory
        response: ChatResponse = chat(model=self.specific_model_name, messages=[
            {
                'role': 'user',
                'content': prompt,
                'images': [image_path]
                # 'additional_kwargs': {"images": [image_path]} # Ollama currently does not support image paths directly
            },
        ])
        return response.message.content

    def close_model(self):
        self.client.generate(model=self.specific_model_name, prompt='', options={'keep_alive': 0})
        service = None

# Ollama vision model can use images: https://github.com/ollama/ollama-python/issues/283
# https://github.com/ollama/ollama-python/blob/main/examples/multimodal-chat.py

