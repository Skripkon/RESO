from werkzeug.utils import secure_filename
from utils.midi2mp3 import midi2mp3

from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import HTTPException
from fastapi import Form

app = FastAPI()

# Configure Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Mount the static directory to serve static files (like CSS, JS, images, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)