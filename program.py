'''
Initiates the VLM captioning server based on user-specified model.
Captions all images in a directory.

# Usage:
# python program.py --model <model_name> --directory <directory_path> --prompt <prompt_name> [--append_prompt <append_prompt>]
'''

import service_selection, argparse, sys, os

def show_models_and_prompts():
    print("Available Models:")
    for model in service_selection.available_service_models.keys():
        print(f" - {model}: {service_selection.available_service_models[model].description}")
    print("\nAvailable Prompts:")
    for prompt in service_selection.available_prompts.keys():
        print(f" - {prompt}: {service_selection.available_prompts[prompt]}")

def get_image_files_from_directory(directory):
    if not os.path.isdir(directory):
        raise ValueError(f"Directory '{directory}' does not exist or is not a directory.")
    supported_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff')
    return [os.path.join(directory, f) for f in os.listdir(directory) if f.lower().endswith(supported_extensions)]

def create_image_text_file(image_path, caption):
    text_file_path = os.path.splitext(image_path)[0] + ".txt"
    with open(text_file_path, 'w', encoding='utf-8') as f:
        f.write(caption)

parser = argparse.ArgumentParser(description="VLM Caption Server")
parser.add_argument('--model', type=str, required=True, help='Model to use for captioning')
parser.add_argument('--directory', type=str, required=True, help='Directory containing images to caption')
parser.add_argument('--prompt', type=str, required=True, help='Prompt to use for captioning')
parser.add_argument('--append_prompt', type=str, help='Optional additional prompt to append')

if len(sys.argv) == 1:
    show_models_and_prompts()
    print('')
    parser.print_help(sys.stderr)
    sys.exit(1)

args = parser.parse_args()
if args.model not in service_selection.get_available_models():
    raise ValueError(f"Invalid model. Available models are: {', '.join(service_selection.get_available_models())}")
if args.prompt not in service_selection.available_prompts:
    raise ValueError(f"Invalid prompt. Available prompts are: {', '.join(service_selection.available_prompts.keys())}")

prompt = service_selection.available_prompts[args.prompt]
if args.append_prompt:
    prompt += " " + args.append_prompt

image_paths = get_image_files_from_directory(args.directory)
if not image_paths:
    raise ValueError(f"No supported image files found in directory '{args.directory}'.")

service = service_selection.start_service(args.model)

print(f"Found {len(image_paths)} images in directory '{args.directory}'.")
print("Processing images...")

for image_path in image_paths:
    try:
        caption = service_selection.get_caption(image_path, prompt)
        create_image_text_file(image_path, caption)
        print(f"Image: {os.path.basename(image_path)}")
        print(f"Caption: {caption}\n")
    except Exception as e:
        print(f"Error processing image {os.path.basename(image_path)}: {str(e)}")

