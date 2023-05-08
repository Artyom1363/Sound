FROM python:3.9

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install gdown

COPY ./ ./

RUN pip install -e .

EXPOSE 8000

CMD ["python3", "online_inference/server.py", "--prod"]


