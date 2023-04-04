FROM python:3.10

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip3 install --no-cache-dir --upgrade -r /code/requirements.txt && pip3 cache purge && rm /usr/local/lib/python3.10/site-packages/df/utils.py
ADD https://raw.githubusercontent.com/Rikorose/DeepFilterNet/main/DeepFilterNet/df/utils.py /usr/local/lib/python3.10/site-packages/df/utils.py
COPY ./app /code/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
