# Use the official Python image as the base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /

# Copy the requirements.txt file into the container
COPY requirements.txt requirements.txt

# Install required packages
RUN apt-get update \
    && apt-get install -y --fix-missing fluidsynth ffmpeg musescore3 libqt5core5a \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* 

# Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the application code into the container

COPY . .

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
