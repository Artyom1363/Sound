FROM python:3.9

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# CMD  bash
# CMD export PYTHONPATH=$PYTHONPATH:/usr/src/app
# CMD pwd
# CMD python3 online_inference/server.py
