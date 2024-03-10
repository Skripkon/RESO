# RESO: Algorithmic and Neural Piano Music Generator

All the information you need is on our website!
[80.78.243.117:8000/](http://80.78.243.117:8000/)

Or here, but opening it may take a while due to inactivity.
[reso.onrender.com/](https://reso.onrender.com/)

## Table of Contents

- [Setup](#Setup)
- [Usage](#Usage)

## Setup

### Via Docker:

1. Build a Docker Image:

```sudo docker build -t deploy-reso .```

2. Run a Docker container:

```sudo docker run -p 8000:8000 deploy-reso```

### Without Docker:

1. Upgrade pip and install Python dependencies

```pip install --no-cache-dir --upgrade -r requirements.txt```

2. Install system-wide packages:

```apt-get install -y --fix-missing fluidsynth ffmpeg musescore3 libqt5core5a```

3. Run a local server:

```uvicorn main:app --host 0.0.0.0 --port 8000```

## Usage

1. Click *Start generating for free*.
2. Choose a music engine (*algorithmic / neural*).
3. Specify the desired properties of the composion.
4. Listen to this!