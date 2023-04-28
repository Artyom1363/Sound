FROM python:3.9

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y ffmpeg

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY ./src ./src

COPY ./online_inference ./online_inference

COPY setup.py ./

RUN pip install -e .

EXPOSE 8002

CMD ["python3", "online_inference/server.py", "--prod"]