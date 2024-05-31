# RESO: Algorithmic and Neural Piano Music Generator

Our server:

[http://194.169.163.103:8000/](http://194.169.163.103:8000/)


> :warning: Our server (for now) is too weak for Neural Generation. LSTM models take up to 10 min. GPT2 models aren't available. Run the server locally to test these models.

## Table of Contents

- [Setup](#Setup)
- [Usage](#Usage)
- [Run Tests](#Tests)
- [Examples of music](#Examples)

## Setup

![linux_icon](https://github.com/Skripkon/RESO/assets/78466953/cf80bfe7-1595-4260-b9d7-5880df3b14e6)

*Instructions below are for Linux only (it was tested on Ubuntu 20.04+).*

### Via Docker:

1. Build a Docker Image:

```sudo docker build -t deploy-reso .```

2. Run a Docker container:

```sudo docker run -p 8000:8000 deploy-reso```

### Without Docker:

1. Upgrade pip and install Python dependencies:

```pip install --no-cache-dir --upgrade -r requirements.txt```

2. Install system-wide packages:

```apt-get install -y --fix-missing fluidsynth ffmpeg musescore3 libqt5core5a timidity```

3. Run a local server:

```uvicorn main:app --host 127.0.0.1 --port 8000```


## Usage

1. Click *Start generating for free*.
2. Choose a music engine (*algorithmic / neural*).
3. Specify the desired properties of the composion.
4. Listen to this!


## Tests

For local testing (you don't need to run the server beforehand):

```python3 run_tests.py --port 8000 --run-server```

*For more info run* `python3 run_tests.py --help`

**Note** that we use [Selenium](https://www.selenium.dev/), which requires Google Chrome to be installed on your machine.
You can install it with the following commands:

```wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb```

```dpkg -i google-chrome-stable_current_amd64.deb; apt-get -fy install```


## Examples

**No cherry picking**

- Model: Waltz. Tempo: Fast. Scale: C.

https://github.com/Skripkon/RESO/assets/78466953/a0dc32c7-c96d-44bf-b442-9d495d744c21

- Model: Etude. Tempo: Normal. Scale: E.

https://github.com/Skripkon/RESO/assets/78466953/2b799837-7927-4fe4-911f-16a2397211a4

- Model: Calm Music. Tempo: Slow. Scale: F#.

https://github.com/Skripkon/RESO/assets/78466953/34e12d50-c5c9-4cb5-a170-58ffad489fd2

- Model: GPT2-Chopin. Tempo: Normal. Scale correction: no.

https://github.com/Skripkon/RESO/assets/78466953/74e8f41e-bf5f-40a8-8200-bd89cb372338

- Model: LSTM-Mozart. Tempo: Fast. Scale correction: no.

https://github.com/Skripkon/RESO/assets/78466953/07b960bb-aa2c-4aae-89b0-a00d2d994e43
