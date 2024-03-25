FROM bash


RUN apk add python3 py3-pip
RUN apk add git
RUN apk add ffmpeg

WORKDIR /xtts-server
COPY ./xtts-streaming-server/test/requirements.txt ./reqs.txt

RUN python -m pip install -r ./reqs.txt

COPY ./xtts-streaming-server ./

CMD ["python","demo.py"]
