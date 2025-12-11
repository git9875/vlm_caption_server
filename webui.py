'''
This is the web user interface for the Image Captioning API.
This creates a 'webui' route in the FastAPI service (api.py).
It serves a simple HTML page allowing users to select models, upload images, and receive captions.
'''
from fastapi import APIRouter, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from service_selection import get_available_models, available_service_models, available_prompts
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/webui", tags=["webui"])
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    available_models = get_available_models()
    models_simplified = {model: available_service_models[model].description for model in available_models}
    return templates.TemplateResponse("index.html", {"request": request, "available_models": models_simplified, "available_prompts":available_prompts})
