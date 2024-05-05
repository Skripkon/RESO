from werkzeug.utils import secure_filename
from generators.algorithmic.Generator01 import generate_music01
from generators.algorithmic.Generator02 import generate_music02
from generators.neural.lstm.Generator import generate_neural
from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import HTTPException
from fastapi import BackgroundTasks
from pydantic import BaseModel
from utils.download_models_and_data import request_to_sownload_files
from utils.audio_editing import edit_mp3, str_to_secs
from utils.data_logging import log_data
from utils.midi2mp3 import midi2mp3
import subprocess
import random
import os
import datetime


# data validation model
class ProcessStart(BaseModel):
    generator: str
    duration: str
    tempo: str
    correct_scale: bool = False
    scale: int = 60


# data validation model
class Editing(BaseModel):
    file: str
    start: str
    end: str
    fade_in: str
    fade_out: str


# data validation model
class Filename(BaseModel):
    filename: str


MAX_TRACKS = 1

app = FastAPI()

# Configure Jinja2 templates
templates = Jinja2Templates(directory="templates")

progress_map = {}

tracks_number_by_ip = {}

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


@app.post("/generate/process_algorithmic_start")
async def process_algorithmic(background_tasks: BackgroundTasks,
                              request: Request,
                              form: ProcessStart):
    ip_address = request.client.host
    if ip_address in tracks_number_by_ip:
        if tracks_number_by_ip[ip_address] >= MAX_TRACKS:
            return JSONResponse(content={"error":
                                         "Too Many Requests. "
                                         "Please try again later."},
                                status_code=429)
        else:
            tracks_number_by_ip[ip_address] += 1
    else:
        tracks_number_by_ip[ip_address] = 1

    subprocess.run(["bash", "utils/remove_old_files.sh", "60"])

    filename: int = random.randint(1, 100_000_000)
    filepath = os.path.join('generated_data', str(filename) + '.mid')
    while os.path.exists(filepath):
        filename = random.randint(1, 100_000_000)
        filepath = os.path.join('generated_data', str(filename) + '.mid')

    minutes, seconds = map(int, form.duration.split(':'))
    duration_sec = minutes * 60 + seconds

    log_data('utils/log.json', "Algo", form.generator,
             datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    match form.generator:
        case "AlgoGen01":
            background_tasks.add_task(generate_music01,
                                      scale=form.scale,
                                      filename=filename,
                                      progress_map=progress_map,
                                      pulse=form.tempo,
                                      duration_sec=duration_sec)
        case "AlgoGen02":
            background_tasks.add_task(generate_music02,
                                      scale=form.scale,
                                      filename=filename,
                                      progress_map=progress_map,
                                      pulse=form.tempo,
                                      duration_sec=duration_sec)
    return JSONResponse(content={"filename": filename})


# render generated algo track
@app.post("/generate/process_algo_finish")
async def process_algo_finish(request: Request,
                              form: Filename):
    ip_address = request.client.host
    midi2mp3(filename=form.filename)
    filepath = os.path.join('generated_data', str(form.filename) + '.mp3')
    if not os.path.exists(filepath):
        tracks_number_by_ip[ip_address] -= 1
        return JSONResponse(content={"error": "MP3 file not found"},
                            status_code=500)
    tracks_number_by_ip[ip_address] -= 1


# is used to get current generation progress in JS code
@app.post("/progress")
async def progress(form: Filename):
    return {"progress": 100 * float(progress_map.get(form.filename, 0))}


# function that initializes neural track generation as a background task
@app.post("/generate/process_neural_start")
async def process_neural_start(form: ProcessStart,
                               background_tasks: BackgroundTasks,
                               request: Request):
    ip_address = request.client.host
    if ip_address in tracks_number_by_ip:
        if tracks_number_by_ip[ip_address] >= MAX_TRACKS:
            return JSONResponse(content={"error": "Too Many Requests. "
                                         "Please try again later."},
                                status_code=429)
        else:
            tracks_number_by_ip[ip_address] += 1
    else:
        tracks_number_by_ip[ip_address] = 1

    subprocess.run(["bash", "utils/remove_old_files.sh", "60"])
    filename: int = random.randint(1, 100_000_000)
    filepath = os.path.join('generated_data', str(filename) + '.mid')
    while os.path.exists(filepath):
        filename = random.randint(1, 100_000_000)
        filepath = os.path.join('generated_data', str(filename) + '.mid')

    minutes, seconds = map(int, form.duration.split(':'))
    duration_sec = minutes * 60 + seconds

    log_data('utils/log.json', "Neural", form.generator,
             datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    try:
        models_folder = \
            os.path.join('generators', 'neural', 'lstm', 'models',
                         form.generator)
        all_models = os.listdir(models_folder)
        random_model = random.choice(all_models)
        model_path = os.path.join(models_folder, random_model)
    except Exception:
        tracks_number_by_ip[ip_address] -= 1
        return JSONResponse(content={"error": "Model file not found"},
                            status_code=500)

    if not os.path.exists(model_path):
        tracks_number_by_ip[ip_address] -= 1
        return JSONResponse(content={"error": "Model file not found"},
                            status_code=500)

    progress_map[filename] = 0
    background_tasks.add_task(generate_neural,
                              composer=form.generator,
                              model_path=model_path,
                              filename=filename,
                              tempo=form.tempo,
                              duration=duration_sec,
                              correct_scale=form.correct_scale,
                              progress_map=progress_map
                              )
    return JSONResponse(content={"filename": filename})


# render generated neural track
@app.post("/generate/process_neural_finish")
async def process_neural_finish(request: Request, form: Filename):
    ip_address = request.client.host

    midi2mp3(filename=form.filename)

    filepath = os.path.join('generated_data', str(form.filename) + '.mp3')
    if not os.path.exists(filepath):
        tracks_number_by_ip[ip_address] -= 1
        return JSONResponse(content={"error": "MP3 file not found"},
                            status_code=500)
    tracks_number_by_ip[ip_address] -= 1


@app.post("/generate/edit")
async def edit(request: Editing):

    subprocess.run(["bash", "utils/remove_old_files.sh", "60"])

    edit_id: int = random.randint(1, 100_000_000)
    file_path = os.path.abspath(request.file)
    export_path = os.path.join(os.path.dirname(
        file_path), "edited_" + os.path.basename(file_path).
            split('.')[0] + f'_{edit_id}.mp3')
    while os.path.exists(export_path):
        edit_id: int = random.randint(1, 100_000_000)
        file_path = os.path.abspath(request.file)
        export_path = os.path.join(os.path.dirname(
            file_path), "edited_" + os.path.basename(file_path).
                split('.')[0] + f'_{edit_id}.mp3')

    edited_file = edit_mp3(request.file,
                           str_to_secs(request.start),
                           str_to_secs(request.end),
                           edit_id,
                           int(request.fade_in),
                           int(request.fade_out))
    print(export_path)
    if not os.path.exists(export_path):
        return JSONResponse(content={"error": "Edited file not found"},
                            status_code=500)

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
