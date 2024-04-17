# RESO: Algorithmic and Neural Piano Music Generator

All the information you need is on our website!
[80.78.243.117:8000/](http://80.78.243.117:8000/)

Or here, but opening it may take a while due to inactivity.
[reso.onrender.com/](https://reso.onrender.com/)

## Table of Contents

- [Setup](#Setup)
- [Usage](#Usage)

## Setup

![linux_icon](https://github.com/Skripkon/RESO/assets/78466953/cf80bfe7-1595-4260-b9d7-5880df3b14e6)

*Instructions below are for Linux only (it was tested on Ubuntu 20.04+)*

*Instructions for MacOS will be added soon...*

### Via Docker:

1. Build a Docker Image:

```sudo docker build -t deploy-reso .```

2. Run a Docker container:

```sudo docker run -p 8000:8000 deploy-reso```

### Without Docker (also works for Windows):

1. Upgrade pip and install Python dependencies

```pip install --no-cache-dir --upgrade -r requirements.txt```

2. Install system-wide packages:

```apt-get install -y --fix-missing fluidsynth ffmpeg musescore3 libqt5core5a```

3. Run a local server:

```uvicorn main:app --host 0.0.0.0 --port 8000```
  
&nbsp;&nbsp;&nbsp;&nbsp;*If the above does not work for you (might be the case on Windows), try*

```uvicorn main:app --host 127.0.0.1 --port 8000```

## Usage

1. Click *Start generating for free*.
2. Choose a music engine (*algorithmic / neural*).
3. Specify the desired properties of the composion.
4. Listen to this!
