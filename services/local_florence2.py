'''
These models do not tag images well, even though it performs simple object detection.
https://huggingface.co/microsoft/Florence-2-base-ft

Microsoft's Florence-2 is currently broken or incompatible with the latest transformers library.
This uses david-littlefield's fix/fork from:  https://github.com/huggingface/transformers/issues/39974#issuecomment-3251539207
https://huggingface.co/ducviet00/Florence-2-base-hf
'''
from ..classes import model_service_abstract
from PIL import Image
from transformers import Florence2Processor, Florence2ForConditionalGeneration
import torch


class model_service(model_service_abstract):
    device = "cpu"
    torch_dtype = torch.float32
    specific_model_name = ""
    model = None
    processor = None

    def __init__(self, specific_model_name):
        self.specific_model_name = specific_model_name
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    def load_model(self):
        self.model = Florence2ForConditionalGeneration.from_pretrained(self.specific_model_name, torch_dtype=self.torch_dtype, trust_remote_code=True).eval().cuda()
        self.processor = Florence2Processor.from_pretrained(self.specific_model_name, trust_remote_code=True)

    def florence2_translate_prompt(self, prompt):
        # Florence-2-base-ft uses codes instead of natural language prompts
        # see https://huggingface.co/microsoft/Florence-2-large/blob/main/sample_inference.ipynb
        code = ''
        match prompt.lower():
            case p if "detail" in p:
                code = "<MORE_DETAILED_CAPTION>"
            case p if "brief" in p:
                code = "<DETAILED_CAPTION>"
            case p if "tags" in p:
                code = "<OD>" # note this is "object detection" and tags may not be listed in order of relevance
            case _:
                code = "<DETAILED_CAPTION>"  # default to detailed
        return code

    def run_inference(self, image_path, prompt):
        # this model doesn't use much memory, so async would be fine, except that it would break dependencies
        if self.model is None or self.processor is None:
            raise RuntimeError("Model has not been instantiated.")
        
        prompt = self.florence2_translate_prompt(prompt)
        image = Image.open(image_path).convert("RGB")
        print(f"run_inference {self.device} {self.torch_dtype}")
        inputs = self.processor(text=prompt, images=image, return_tensors="pt").to(self.device, self.torch_dtype)
        generated_ids = self.model.generate(
            input_ids=inputs["input_ids"],
            pixel_values=inputs["pixel_values"],
            max_new_tokens=1024,
            do_sample=False,
            num_beams=3
        )
        generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=False)[0]
        parsed_answer = self.processor.post_process_generation(generated_text, task=prompt, image_size=(image.width, image.height))
        print("Parsed answer:", parsed_answer)

        if prompt == "<OD>":
            return ', '.join(parsed_answer[prompt]['labels'])
        return parsed_answer[prompt]

    def close_model(self):
        self.model = None
        self.processor = None
        self.specific_model_name = ""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
