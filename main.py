from werkzeug.utils import secure_filename
from generators.algorithmic.Generator01 import generate_music01
from generators.algorithmic.Generator02 import generate_music02
from generators.neural.lstm.Generator import generate_neural
from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import HTTPException
from fastapi import Form
from utils.download_models_and_data import request_to_sownload_files
from utils.audio_editing import edit_mp3, str_to_secs
from utils.data_logging import log_data
from utils.midi2mp3 import midi2mp3
import random
import os
import datetime

os.environ['QT_QPA_PLATFORM'] = 'offscreen'

app = FastAPI()

# Configure Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Mount the static directory to serve static files (like CSS, JS, images, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.mount("/generated_data", StaticFiles(directory="generated_data"),
          name="generated_data")

request_to_sownload_files()


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})


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
    return FileResponse(mp3_file_path, media_type='audio/mpeg',
                        filename='converted.mp3')


@app.get("/generate", response_class=HTMLResponse)
async def generate(request: Request):
    return templates.TemplateResponse("generate.html", {"request": request})


@app.get("/generate/algorithmic", response_class=HTMLResponse)
async def algorithmic_page(request: Request):
    return templates.TemplateResponse("algorithmic.html", {"request": request})


@app.get("/generate/neural", response_class=HTMLResponse)
async def neural_page(request: Request):
    return templates.TemplateResponse("neural.html", {"request": request})


@app.post("/generate/process_algorithmic")
async def process_algorithmic(generator: str = Form(...),
                              duration: str = Form(...),
                              tempo: str = Form(...),
                              scale: int = Form(...)):

    filename: int = random.randint(1, 100_000_000)

    minutes, seconds = map(int, duration.split(':'))
    duration_sec = minutes * 60 + seconds

    log_data('utils/log.json', "Algo", generator,
             datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    match generator:
        case "AlgoGen01":
            generate_music01(scale=scale,
                             filename=filename,
                             pulse=tempo,
                             duration_sec=duration_sec)
        case "AlgoGen02":
            generate_music02(scale=scale,
                             filename=filename,
                             pulse=tempo,
                             duration_sec=duration_sec)

    midi2mp3(filename=filename)
    return JSONResponse(content={"filename": filename})


@app.post("/generate/process_neural")
async def process_neural(generator: str = Form(...),
                         duration: str = Form(...),
                         tempo: str = Form(...)):

    filename: int = random.randint(1, 100_000_000)
    minutes, seconds = map(int, duration.split(':'))
    duration_sec = minutes * 60 + seconds

    log_data('utils/log.json', "Neural", generator,
             datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    models_folder = \
        os.path.join('generators', 'neural', 'lstm', 'models', generator)
    all_models = os.listdir(models_folder)
    random_model = random.choice(all_models)
    model_path = os.path.join(models_folder, random_model)

    generate_neural(composer=generator,
                    model_path=model_path,
                    filename=filename,
                    tempo=tempo,
                    duration=duration_sec,
                    correct_scale=True
                    )
    midi2mp3(filename=filename)
    return JSONResponse(content={"filename": filename})


@app.post("/generate/edit")
async def edit(file: str = Form(...),
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
async def download_generated_file_midi(filename: str):
    file_path = os.path.join("generated_data", filename)
    return FileResponse(file_path, media_type='audio/midi', filename=filename)


@app.get("/downloadMP3/{filename}")
async def download_generated_file_mp3(filename: str):
    file_path = os.path.join("generated_data", filename)
    return FileResponse(file_path, media_type='audio/mpeg', filename=filename)


@app.get("/downloadMusicXML/{filename}")
async def download_generated_file_xml(filename: str):
    file_path = os.path.join("generated_data", filename)
    return FileResponse(file_path,
                        media_type='application/vnd.recordare.musicxml+xml',
                        filename=filename)


@app.get("/downloadPDF/{filename}")
async def download_generated_file_pdf(filename: str):
    file_path = os.path.join("generated_data", filename)
    return FileResponse(file_path, media_type='application/pdf',
                        filename=filename)


@app.get("/downloadEditedMP3/{filename}")
async def download_edited_file(filename: str):
    file_path = os.path.join("generated_data", filename)
    return FileResponse(file_path, media_type='audio/midi', filename=filename)


@app.get("/help/generators_type", response_class=HTMLResponse)
async def help_generators_type(request: Request):
    return templates.TemplateResponse("help_generators_type.html",
                                      {"request": request})


@app.get("/about_us", response_class=HTMLResponse)
async def about_us(request: Request):
    return templates.TemplateResponse("about_us.html",
                                      {"request": request})
