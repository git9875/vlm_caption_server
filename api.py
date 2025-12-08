'''
This is a FastAPI server that handles requests and calls the service selection module.
It exposes endpoints for captioning images using various models.
'''
import os
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import service_selection, webui
from classes import caption_directory_job

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(webui.router)

class InitiateService(BaseModel):
    service_model: str

class CaptionFileRequest(BaseModel):
    image_path: str
    prompt: str
    append_prompt: Optional[str] = None

class CaptionDirectoryRequest(BaseModel):
    directory: str
    prompt: str
    append_prompt: Optional[str] = None

# caption directory requests can only operate on one directory job at a time
caption_job = None


@app.post("/load_model_service")
async def load_model_service(request: InitiateService):
    try:
        if service_selection.selected_service_model is not None:
            service_selection.close_service()
        service_selection.start_service(request.service_model)
        return {"message": f"Service '{request.service_model}' started successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# individual image captioning
@app.post("/caption")
async def caption_image(request: CaptionFileRequest):
    try:
        full_prompt = f"{request.prompt} {request.append_prompt}" if request.append_prompt else request.prompt
        caption = service_selection.get_caption(request.image_path, full_prompt)
        return {"caption": caption}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/available_models")
async def get_available_models():
    models = {}
    for m in service_selection.available_service_models:
        models[m] = service_selection.available_service_models[m].description
    return {"available_models": models}

@app.get("/available_prompts")
async def get_available_prompts():
    return {"available_prompts": service_selection.available_prompts}

@app.get("/")
async def root():
    return {"message": "Welcome to the Image Captioning API"}

def file_is_image(file_path):
    valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
    _, ext = os.path.splitext(file_path.lower())
    valid = ext in valid_extensions
    return ext in valid_extensions

def list_files_directory(directory: str):
    if not os.path.isdir(directory):
        raise ValueError(f"Directory '{directory}' does not exist or is not a directory.")
    # this list comprehension with multiple conditions was giving me trouble
    # return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f) and file_is_image(f))]
    files = []
    for f in os.listdir(directory):
        full_path =  os.path.join(directory, f)
        if os.path.isfile(full_path) and file_is_image(full_path):
            files.append(f)
    return files

def create_caption_file(image_path, caption):
    text_file_path = os.path.splitext(image_path)[0] + ".txt"
    with open(text_file_path, 'w', encoding='utf-8') as f:
        f.write(caption)

@app.post("/caption_directory")
async def caption_directory(request: CaptionDirectoryRequest, background_tasks: BackgroundTasks):
    global caption_job
    if caption_job and caption_job.total_files > caption_job.processed_files:
        raise HTTPException(status_code=409, detail="A captioning job is already in progress")
        
    try:
        actual_prompt = service_selection.available_prompts[request.prompt]
        full_prompt = f"{actual_prompt} {request.append_prompt}" if request.append_prompt else actual_prompt
        files = list_files_directory(request.directory)
        caption_job = caption_directory_job(files)

        def process_files():
            for file in files:
                if caption_job is None:
                    raise HTTPException(status_code=409, detail="No captioning job is in progress")
                file_path = os.path.join(request.directory, file)
                caption_job.update_file_status(file, "Processing", '')
                try:
                    caption = service_selection.get_caption(file_path, full_prompt)
                    create_caption_file(file_path, caption)
                    caption_job.update_file_status(file, "Success", caption)
                except Exception as e:
                    caption_job.update_file_status(file, "Error", str(e))

        background_tasks.add_task(process_files)
        return {"message": "Captioning process started in the background", "files": files}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stop_model_service")
async def stop_model_service():
    await stop_job()
    if service_selection.selected_service_model is not None:
        service_selection.close_service()
    return {"message": "Model service stopped"}

@app.post("/stop_job")
async def stop_job():
    global caption_job
    if caption_job is not None:
        caption_job = None
    return {"message": "Job stopped"}

@app.get("/caption_directory_status")
async def caption_directory_status():
    global caption_job
    if caption_job is None:
        raise HTTPException(status_code=409, detail="No captioning job is in progress")
    return caption_job.get_progress()
