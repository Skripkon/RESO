import datetime
import os
import random
import subprocess

from fastapi import BackgroundTasks
from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from generators.algorithmic.Generator01 import generate_music01
from generators.algorithmic.Generator02 import generate_music02
from generators.algorithmic.Generator03 import generate_music03
from generators.neural.lstm.NeuralGenerator import generate_neural
from pydantic import BaseModel
from utils.audio_editing import edit_mp3, str_to_secs
from utils.data_logging import log_data
from utils.download_models_and_data import request_to_download_files
from utils.midi2mp3 import midi2mp3
from werkzeug.utils import secure_filename


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
    filename: int


# tracks that were edited longer than this many minutes ago will be deleted
DELETION_THRESHOLD = 10
# number of tracks that can be generated per IP address at the same time
MAX_TRACKS = 1

tracks_number_by_ip = {}
progress_map = {}

app = FastAPI()

# Configure Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Mount the static directory to serve static files (like CSS, JS, images, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.mount("/generated_data", StaticFiles(directory="generated_data"), name="generated_data")

request_to_download_files()


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request, "main.html")


@app.post('/convert_midi2mp3')
async def convert_midi2mp3(form: Filename):
    if not form:
        raise HTTPException(status_code=400, detail='No file part')

    if str(form.filename) == '':
        raise HTTPException(status_code=400, detail='No selected file')

    filename = secure_filename(str(form.filename))
    with open(filename, 'wb') as f:
        f.write(str(form.filename).read())

    mp3_file_path = midi2mp3(filename)
    return FileResponse(mp3_file_path, media_type='audio/mpeg', filename='converted.mp3')


@app.get("/generate", response_class=HTMLResponse)
async def generate(request: Request):
    return templates.TemplateResponse(request, "generate.html")


@app.get("/generate/algorithmic", response_class=HTMLResponse)
async def algorithmic_page(request: Request):
    return templates.TemplateResponse(request, "algorithmic.html")


@app.get("/generate/neural", response_class=HTMLResponse)
async def neural_page(request: Request):
    return templates.TemplateResponse(request, "neural.html")


# is used to get current generation progress in JS code
@app.post("/progress")
async def progress(form: Filename):
    return {"progress": 100 * float(progress_map.get(form.filename, 0))}


def max_generations_count_surpass(ip_address: str):
    """
    Checks whether the user has already reached synchronous generation
    limit set by constant MAX_TRACK.
    """
    tracks_number_by_ip[ip_address] = tracks_number_by_ip.get(ip_address, 0) + 1
    if tracks_number_by_ip[ip_address] > MAX_TRACKS:
        tracks_number_by_ip[ip_address] -= 1
        return True
    return False


def get_filename():
    """
    Generates a random int to be used as a filename avoiding collisions.
    """
    filename: int = random.randint(1, 100_000_000)
    filepath = os.path.join('generated_data', str(filename) + '.mid')
    while os.path.exists(filepath):
        filename = random.randint(1, 100_000_000)
        filepath = os.path.join('generated_data', str(filename) + '.mid')
    return filename


# task to be added as a background task for algorithmic generation
# generates the track and subtracts 1 from the according track count
def generate_algo_task(generator,
                       scale,
                       filename,
                       progress_map,
                       pulse,
                       duration_sec,
                       ip_address):
    if generator == "AlgoGen01":
        generate_music01(scale=scale,
                         filename=filename,
                         progress_map=progress_map,
                         pulse=pulse,
                         duration_sec=duration_sec
                         )
    elif generator == "AlgoGen02":
        generate_music02(scale=scale,
                         filename=filename,
                         progress_map=progress_map,
                         pulse=pulse,
                         duration_sec=duration_sec
                         )
    elif generator == "AlgoGen03":
        generate_music03(scale=scale,
                         filename=filename,
                         progress_map=progress_map,
                         pulse=pulse,
                         duration_sec=duration_sec
                         )
    tracks_number_by_ip[ip_address] -= 1


# function that initializes algorithmic track generation as a background task
@app.post("/generate/process_algorithmic_start")
async def process_algorithmic(background_tasks: BackgroundTasks,
                              request: Request,
                              form: ProcessStart):
    ip_address = request.client.host
    if max_generations_count_surpass(ip_address):
        return JSONResponse(content={"error": "You have a generation running. Please try again later."},
                            status_code=429)

    subprocess.run(["bash", "utils/remove_old_files.sh", str(DELETION_THRESHOLD)])

    filename: int = get_filename()

    minutes, seconds = map(int, form.duration.split(':'))
    duration_sec = minutes * 60 + seconds

    log_data('utils/log.json', "Algo", form.generator, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    background_tasks.add_task(generate_algo_task,
                              generator=form.generator,
                              scale=form.scale,
                              filename=filename,
                              progress_map=progress_map,
                              pulse=form.tempo,
                              duration_sec=duration_sec,
                              ip_address=ip_address)
    return JSONResponse(content={"filename": filename})


# task to be added as a background task for neural generation
# generates the track and subtracts 1 from the according track count
def generate_neural_task(composer,
                         model_path,
                         filename,
                         tempo,
                         duration,
                         correct_scale,
                         progress_map,
                         ip_address
                         ):
    generate_neural(composer=composer,
                    model_path=model_path,
                    filename=filename,
                    tempo=tempo,
                    duration=duration,
                    correct_scale=correct_scale,
                    progress_map=progress_map
                    )
    tracks_number_by_ip[ip_address] -= 1


# function that initializes neural track generation as a background task
@app.post("/generate/process_neural_start")
async def process_neural_start(background_tasks: BackgroundTasks,
                               request: Request,
                               form: ProcessStart):
    ip_address = request.client.host
    if max_generations_count_surpass(ip_address):
        return JSONResponse(content={"error": "You have a generation running. Please try again later."},
                            status_code=429)

    subprocess.run(["bash", "utils/remove_old_files.sh", str(DELETION_THRESHOLD)])

    filename: int = get_filename()

    minutes, seconds = map(int, form.duration.split(':'))
    duration_sec = minutes * 60 + seconds

    log_data('utils/log.json', "Neural", form.generator,
             datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    try:
        models_folder = \
            os.path.join('generators', 'neural', 'lstm',
                         'models', form.generator)
        all_models = os.listdir(models_folder)
        random_model = random.choice(all_models)
        model_path = os.path.join(models_folder, random_model)
    except Exception:
        tracks_number_by_ip[ip_address] -= 1
        return JSONResponse(content={"error": "Model file not found"}, status_code=500)

    if not os.path.exists(model_path):
        tracks_number_by_ip[ip_address] -= 1
        return JSONResponse(content={"error": "Model file not found"}, status_code=500)

    progress_map[filename] = 0
    background_tasks.add_task(generate_neural_task,
                              composer=form.generator,
                              model_path=model_path,
                              filename=filename,
                              tempo=form.tempo,
                              duration=duration_sec,
                              correct_scale=form.correct_scale,
                              progress_map=progress_map,
                              ip_address=ip_address
                              )
    return JSONResponse(content={"filename": filename})


# render generated track
@app.post("/generate/process_track_finish")
async def process_track_finish(form: Filename):
    if not os.path.exists(os.path.join('generated_data', f'{str(form.filename)}.mid')):
        return JSONResponse(content={"error": "MIDI file not found"}, status_code=500)

    midi2mp3(filename=form.filename)
    filepath = os.path.join('generated_data', str(form.filename) + '.mp3')
    if not os.path.exists(filepath):
        return JSONResponse(content={"error": "MP3 file not found"}, status_code=500)


def get_edit_id(filename: int):
    """
    Generates a random int to be used for a filename avoiding collisions.
    """
    edit_id: int = random.randint(1, 100_000_000)
    edit_filename = f'edited_{filename}_{edit_id}.mp3'
    while os.path.exists(os.path.join('generated_data', edit_filename)):
        edit_id: int = random.randint(1, 100_000_000)
        edit_filename = f'edited_{filename}_{edit_id}.mp3'
    return edit_id


@app.post("/generate/edit")
async def edit(form: Editing):

    subprocess.run(["bash", "utils/remove_old_files.sh",
                    str(DELETION_THRESHOLD)])

    edit_id: int = get_edit_id(filename=int(os.path.basename(form.file).split('.')[0]))
    edited_file = edit_mp3(form.file,
                           str_to_secs(form.start),
                           str_to_secs(form.end),
                           edit_id,
                           int(form.fade_in),
                           int(form.fade_out))

    if not os.path.exists(os.path.join('generated_data', edited_file)):
        return JSONResponse(content={"error": "Edited file not found"}, status_code=500)

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
    return FileResponse(file_path, media_type='application/vnd.recordare.musicxml+xml', filename=filename)


@app.get("/downloadPDF/{filename}")
async def download_generated_file_pdf(filename: str):
    file_path = os.path.join("generated_data", filename)
    return FileResponse(file_path, media_type='application/pdf', filename=filename)


@app.get("/downloadEditedMP3/{filename}")
async def download_edited_file(filename: str):
    file_path = os.path.join("generated_data", filename)
    return FileResponse(file_path, media_type='audio/mpeg', filename=filename)


@app.get("/help/generators_type", response_class=HTMLResponse)
async def help_generators_type(request: Request):
    return templates.TemplateResponse(request, "help_generators_type.html")


@app.get("/about_us", response_class=HTMLResponse)
async def about_us(request: Request):
    return templates.TemplateResponse(request, "about_us.html")
