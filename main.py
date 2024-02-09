from werkzeug.utils import secure_filename
from utils.midi2mp3 import midi2mp3
from generators.algorithmic.Generator01 import generate_music01

from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import HTTPException
from fastapi import Form
import os

app = FastAPI()

# Configure Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Mount the static directory to serve static files (like CSS, JS, images, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.mount("/generated_data", StaticFiles(directory="generated_data"),
          name="generated_data")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})


@app.get("/editing", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("editing.html", {"request": request})


@app.get("/convert", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("convert.html", {"request": request})


@app.post('/convert_midi2mp3')
async def convert_midi2mp3(midi_file: UploadFile = File(...)):
    if not midi_file:
        raise HTTPException(status_code=400, detail='No file part')

    if midi_file.filename == '':
        raise HTTPException(status_code=400, detail='No selected file')

    filename = secure_filename(midi_file.filename)
    with open(filename, 'wb') as f:
        f.write(midi_file.file.read())

    mp3_file_path = midi2mp3(filename)
    return FileResponse(mp3_file_path, media_type='audio/mpeg', filename='converted.mp3')


@app.get("/generate", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("generate.html", {"request": request})


@app.get("/generate/algorithmic", response_class=HTMLResponse)
async def algorithmic_page(request: Request):
    return templates.TemplateResponse("algorithmic.html", {"request": request})


@app.get("/generate/neural", response_class=HTMLResponse)
async def neural_page(request: Request):
    return templates.TemplateResponse("neural.html", {"request": request})


@app.post("/generate/process_algorithmic")
async def process_algorithmic(generator: str = Form(...)):
    file_path = os.path.join("generated_data", "generated_track.mid")
    if generator == "AlgoGen01":
        generate_music01(59, file_path)
        mp3_file_path = midi2mp3(file_path)
        return FileResponse(mp3_file_path, media_type='audio/mpeg', filename='generated_track.mp3')


@app.post("/generate/generated_track", response_class=HTMLResponse)
async def generated_track(request: Request):
    return templates.TemplateResponse("generated_track.html", {"request": request})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)
