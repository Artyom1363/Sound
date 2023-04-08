FROM python:3.9

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y ffmpeg

COPY . .

RUN pip install -e .

EXPOSE 8001

CMD ["python3", "online_inference/server.py"]

# CMD  bash
# CMD export PYTHONPATH=$PYTHONPATH:/usr/src/app
# CMD pwd
# CMD python3 online_inference/server.py