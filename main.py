from werkzeug.utils import secure_filename
from utils.midi2mp3 import midi2mp3
from generators.algorithmic.Generator01 import generate_music01
from generators.algorithmic.Generator02 import generate_music02
import random
from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import HTTPException
from fastapi import Form
from pydantic import BaseModel
from utils.audio_editing import edit_mp3, str_to_secs
from utils.data_logging import log_data
import os
import datetime

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
async def process_algorithmic(generator: str = Form(...), duration: str = Form(...), tempo: str = Form(...), scale: int = Form(...)):
    name_of_the_file: int = random.randint(1, 100_000_000)

    minutes, seconds = map(int, duration.split(':'))
    duration_sec = minutes * 60 + seconds

    log_data('utils/log.json', "Algo", generator,
             datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    if generator == "AlgoGen01":
        generate_music01(scale=scale, name_of_the_file=name_of_the_file)
        midi2mp3(name_of_the_file=name_of_the_file)
        return JSONResponse(content={"filename": name_of_the_file})
    elif generator == "AlgoGen02":
        generate_music02(scale=scale,  name_of_the_file=name_of_the_file, pulse=tempo, duration_sec=duration_sec)
        midi2mp3(name_of_the_file=name_of_the_file)
        return JSONResponse(content={"filename": name_of_the_file})


@app.post("/generate/edit_algorithmic")
async def edit_algorithmic(file: str = Form(...),
                           start: str = Form(...),
                           end: str = Form(...),
                           fade_in: str = Form(...),
                           fade_out: str = Form(...)):
    edit_id: int = random.randint(1, 100_000_000)
    edited_file = edit_mp3(file,
                           str_to_secs(start),
                           str_to_secs(end),
                           edit_id,
                           int(fade_in),
                           int(fade_out))
    return JSONResponse(content={"file": edited_file})


@app.get("/downloadMID/{filename}")
async def download_generated_file(filename: str):
    file_path = os.path.join("generated_data", filename)
    return FileResponse(file_path, media_type='audio/midi', filename=filename)


@app.get("/downloadMP3/{filename}")
async def download_generated_file(filename: str):
    file_path = os.path.join("generated_data", filename)
    return FileResponse(file_path, media_type='audio/mpeg', filename=filename)

@app.get("/downloadMusicXML/{filename}")
async def download_generated_file(filename: str):
    file_path = os.path.join("generated_data", filename)
    return FileResponse(file_path, media_type='application/vnd.recordare.musicxml+xml', filename=filename)

@app.get("/downloadPDF/{filename}")
async def download_generated_file(filename: str):
    file_path = os.path.join("generated_data", filename)
    return FileResponse(file_path, media_type='application/pdf', filename=filename)


@app.get("/downloadEditedMP3/{filename}")
async def download_edited_file(filename: str):
    file_path = os.path.join("generated_data", filename)
    return FileResponse(file_path, media_type='audio/midi', filename=filename)


@app.get("/help/generators_type", response_class=HTMLResponse)
async def neural_page(request: Request):
    return templates.TemplateResponse("help_generators_type.html", {"request": request})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)
