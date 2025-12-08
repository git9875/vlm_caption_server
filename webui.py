'''
This is the web user interface for the Image Captioning API.
This creates a 'webui' route in the FastAPI service (api.py).
It serves a simple HTML page allowing users to select models, upload images, and receive captions.
The HTML page includes a form for uploading images and a dropdown menu for selecting available models.
The HTML page is styled with basic CSS for a clean and user-friendly interface.
It uses JavaScript to handle form submissions and display the caption results.
The page also includes error handling to display any issues that may occur during the captioning process.
The JavaScript code handles the following functionality:
1. Fetching available models from the API and populating the dropdown menu
2. Handling image upload and form submission
3. Displaying the caption results or error messages
4. Providing visual feedback during the captioning process
5. Implementing client-side validation for the form inputs
6. Ensuring the UI remains responsive and provides appropriate feedback to users throughout the process
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
