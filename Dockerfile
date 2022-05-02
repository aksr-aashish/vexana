# We're using Debian Slim Buster image
FROM python:3.8.5-slim-buster

ENV PIP_NO_CACHE_DIR 1

RUN sed -i.bak 's/us-west-2\.ec2\.//' /etc/apt/sources.list

# Pypi package Repo upgrade
RUN pip3 install --upgrade pip setuptools
# Copy Python Requirements to /root/vexana

RUN git clone -b main https://github.com/aksr-aashish/vexana /root/vexana
WORKDIR /root/vexana


RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir --upgrade --requirement requirements.txt
CMD bash start
