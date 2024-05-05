from werkzeug.utils import secure_filename
from generators.algorithmic.Generator01 import generate_music01
from generators.algorithmic.Generator02 import generate_music02
from generators.neural.lstm.Generator import generate_neural
from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import HTTPException
from fastapi import Form, BackgroundTasks
from utils.download_models_and_data import request_to_sownload_files
from utils.audio_editing import edit_mp3, str_to_secs
from utils.data_logging import log_data
from utils.midi2mp3 import midi2mp3
import subprocess
import random
import os
import datetime

MAX_TRACKS = 1

os.environ['QT_QPA_PLATFORM'] = 'offscreen'

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
                              generator: str = Form(...),
                              duration: str = Form(...),
                              tempo: str = Form(...),
                              scale: int = Form(...)):
    ip_address = request.client.host
    if max_generations_count_surpass(ip_address):
        return JSONResponse(content={
            "error": "Too Many Requests. Please try again later."},
            status_code=429)

    subprocess.run(["bash", "utils/remove_old_files.sh", "60"])

    filename: int = random.randint(1, 100_000_000)
    filepath = os.path.join('generated_data', str(filename) + '.mid')
    while os.path.exists(filepath):
        filename = random.randint(1, 100_000_000)
        filepath = os.path.join('generated_data', str(filename) + '.mid')

    minutes, seconds = map(int, duration.split(':'))
    duration_sec = minutes * 60 + seconds

    log_data('utils/log.json', "Algo", generator,
             datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    match generator:
        case "AlgoGen01":
            background_tasks.add_task(generate_music01,
                                      scale=scale,
                                      filename=filename,
                                      progress_map=progress_map,
                                      pulse=tempo,
                                      duration_sec=duration_sec)
        case "AlgoGen02":
            background_tasks.add_task(generate_music02,
                                      scale=scale,
                                      filename=filename,
                                      progress_map=progress_map,
                                      pulse=tempo,
                                      duration_sec=duration_sec)
    return JSONResponse(content={"filename": filename})


# render generated track
@app.post("/generate/process_track_finish")
async def process_track_finish(request: Request,
                               filename: int = Form(...)):
    ip_address = request.client.host
    tracks_number_by_ip[ip_address] -= 1
    midi2mp3(filename=filename)
    filepath = os.path.join('generated_data', str(filename) + '.mp3')
    if not os.path.exists(filepath):
        return JSONResponse(content={"error": "MP3 file not found"},
                            status_code=500)


# is used to get current generation progress in JS code
@app.post("/progress")
async def progress(filename: int = Form(...)):
    return {"progress": 100 * float(progress_map.get(filename, 0))}


def max_generations_count_surpass(ip_address: str):
    tracks_number_by_ip[ip_address] = tracks_number_by_ip.get(ip_address,
                                                              0) + 1
    if tracks_number_by_ip[ip_address] > MAX_TRACKS:
        tracks_number_by_ip[ip_address] -= 1
        print(f"IP address {ip_address} currently has {tracks_number_by_ip[ip_address]} tracks generating")
        return True
    return False


# function that initializes neural track generation as a background task
@app.post("/generate/process_neural_start")
async def process_neural_start(background_tasks: BackgroundTasks,
                               request: Request,
                               generator: str = Form(...),
                               duration: str = Form(...),
                               tempo: str = Form(...),
                               correct_scale: bool = Form(...)):
    ip_address = request.client.host
    if max_generations_count_surpass(ip_address):
        return JSONResponse(content={
            "error": "Too Many Requests. Please try again later."},
            status_code=429)

    subprocess.run(["bash", "utils/remove_old_files.sh", "60"])
    filename: int = random.randint(1, 100_000_000)
    filepath = os.path.join('generated_data', str(filename) + '.mid')
    while os.path.exists(filepath):
        filename = random.randint(1, 100_000_000)
        filepath = os.path.join('generated_data', str(filename) + '.mid')

    minutes, seconds = map(int, duration.split(':'))
    duration_sec = minutes * 60 + seconds

    log_data('utils/log.json', "Neural", generator,
             datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    try:
        models_folder = \
            os.path.join('generators', 'neural', 'lstm', 'models', generator)
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
                              composer=generator,
                              model_path=model_path,
                              filename=filename,
                              tempo=tempo,
                              duration=duration_sec,
                              correct_scale=correct_scale,
                              progress_map=progress_map
                              )
    return JSONResponse(content={"filename": filename})


@app.post("/generate/edit")
async def edit(file: str = Form(...),
               start: str = Form(...),
               end: str = Form(...),
               fade_in: str = Form(...),
               fade_out: str = Form(...)):

    subprocess.run(["bash", "utils/remove_old_files.sh", "60"])

    edit_id: int = random.randint(1, 100_000_000)
    file_path = os.path.abspath(file)
    export_path = os.path.join(os.path.dirname(
        file_path), "edited_" + os.path.basename(file_path).
            split('.')[0] + f'_{edit_id}.mp3')
    while os.path.exists(export_path):
        edit_id: int = random.randint(1, 100_000_000)
        file_path = os.path.abspath(file)
        export_path = os.path.join(os.path.dirname(
            file_path), "edited_" + os.path.basename(file_path).
                split('.')[0] + f'_{edit_id}.mp3')

    edited_file = edit_mp3(file,
                           str_to_secs(start),
                           str_to_secs(end),
                           edit_id,
                           int(fade_in),
                           int(fade_out))
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
