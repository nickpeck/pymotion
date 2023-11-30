FROM ubuntu:20.04
RUN apt update
RUN apt install -y software-properties-common
RUN add-apt-repository -y ppa:deadsnakes/ppa
RUN apt install -y python3.9
RUN apt install -y python3-pip
RUN python3 -m pip install --upgrade pip
RUN apt install -y libsdl2-dev
RUN apt install -y python3-pygame
RUN apt install -y python3-numpy
WORKDIR /usr/src/app
RUN python3 -m pip install --upgrade setuptools wheel
RUN apt install -y libjpeg-dev 
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY src .
RUN apt-get update && apt-get -y install --no-install-recommends \
    libfreetype6-dev \
    libportmidi-dev \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    && rm -rf /var/lib/apt/lists/*
RUN pip install pygame==2.1.2
CMD ["python3", "-m", "pymotion"]

