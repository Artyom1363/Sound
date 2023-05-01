FROM python:3.9

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install gdown

COPY ./src ./src

COPY ./online_inference ./online_inference

COPY setup.py ./

RUN pip install -e .

EXPOSE 8000

CMD ["python3", "online_inference/server.py", "--prod"]


