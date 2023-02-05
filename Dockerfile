FROM python:3.10-bullseye

WORKDIR /app
RUN apt-get update && apt-get install -y \
    automake \
    build-essential \
    curl \
    cmake \
    libgl1 python3-opencv libsm6 libxext6 \
 && rm -rf /var/lib/apt/lists/*
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

CMD [ "python", "./gn_auto.py" ]
