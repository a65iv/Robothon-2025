from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Template configuration
templates = Jinja2Templates(directory="GUI/templates")

@app.get("/", response_class=HTMLResponse)
async def read_ui(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
