# VLM Image Caption Server
Image directory captioning system using VLMs. Run on command line or FastAPI which includes a web interface. Useful for creating image datasets used to train a LoRA.

## Overview
Caption all the images in a directory with downloaded Vision Language Models (VLMs) by using a command line tool or local web service. A simple web UI is included. Caption text files are saved in the same directory as the images, with the same name but with a .txt extension.

## Features
- **Model Selection**: Choose from available VLM models
- **No Uploading**: Images are processed from a local directory.
- **Caption Generation**: Receive captions (short, detailed, or tags) for images
- **User-Friendly Interface**: Clean, responsive design with visual feedback

## Models Currently Included
- [Qwen3-VLM-8B](https://ollama.com/library/qwen3-vl) available through Ollama.
- [Florence-2-base](https://huggingface.co/microsoft/Florence-2-base-ft), but [fixed](https://github.com/huggingface/transformers/issues/39974#issuecomment-3251539207) with transformers using [David Littlefield's models that have identical weights](https://huggingface.co/ducviet00/Florence-2-base-hf), just converted for native support. Note that although Florence-2 does a job at describing images in detail, it does poorly at "tagging" with the `<OD>` task prompt. `local_florence2.py` includes a prompt translation from the coded task prompts, [see the original examples here](https://huggingface.co/microsoft/Florence-2-large/blob/main/sample_inference.ipynb).

## Installation
1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```
3. Activate the virtual environment:
   - On Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```
4. Install dependencies:
   ```bash
   # if you intend to run a model on ollama:
   pip install ollama

   # if you intend to use the web service to connect to it from other programs:
   pip install "fastapi[standard]" uvicorn jinja2
   # jinja2 is needed for the simple web UI template

   # if you are going to use any Huggingface models running locally:
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128
   pip install torch transformers Pillow einops timm
   ```
5. If using Ollama to serve [Qwen3-VLM-8b](https://ollama.com/library/qwen3-vl):
   ```bash
   ollama pull qwen3-vl:8b  
   ```

## Usage
- Start the FastAPI server:
   ```bash
   uvicorn api:app --reload
   ```
   [Read the Swagger UI docs](http://127.0.0.1:8000/docs#/) or [view the web UI](http://127.0.0.1:8000/webui/).
   First, POST request to /load_model_service, and then POST to /caption_directory using 

- Or, you can run the command line tool with:
   ```bash
   python program.py --model [model_name] --directory [image_directory] --prompt [prompt_name]

   # To view the available models and prompts, simply run:
   python program.py
   ```

Screenshot of the web UI:
![Web UI Example](https://example.com/images/sunset.jpg)

## To customize it for other models, you can add new service class, or modify existing ones
- Edit `service_selection.py` to modify available models. Prompts can also be modified.
- Adjust `available_service_models` dictionary to include your preferred vision language models
- In `services` directory, you can add a new service class according to the `model_service_abstract` class in `classes.py`.

Regarding Microsoft's Florence-2-base-ft vision language model, it is currently broken or incompatible with the latest transformers library. This uses [david-littlefield's fix/fork](https://github.com/huggingface/transformers/issues/39974#issuecomment-3251539207).

## Contributing
I am open to suggestions and feedback. If there is a locally-run VLM that is great at captioning images or videos, I may want to include it in this project in the future.
Contributions are welcome! If you encounter any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License
This project is licensed under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0).  
You are free to use, modify, and distribute with minimal restriction.

## Acknowledgements
- AI Code Assist was used in VS Code, presumably through Copilot. It did an amazing job offering suggestions and completing code.
- [Qwen team at Alibaba Cloud](https://qwen.ai/blog?id=99f0335c4ad9ff6153e517418d48535ab6d8afef&from=research.latest-advancements-list)
- [Microsoft](https://www.microsoft.com/) for providing the Florence-2-base-ft vision language model used in this project.
- [David Littlefield](https://huggingface.co/ducviet00/Florence-2-base-hf) for providing the fix/fork for Florence-2-base.
- [Ollama](https://ollama.com/) for providing the locally-run vision language model used in this project.
- [Hugging Face](https://huggingface.co/) for providing the transformers library used in this project.
