FROM python:3.6
# FROM pytorch:1.1.0

ENV APP_HOME /app

WORKDIR $APP_HOME

ENV PYTHONUNBUFFERED True

COPY . ./

RUN wget https://storage.googleapis.com/rsna-classification-model-weights/model_epoch_best_4.zip --no-check-certificate

RUN unzip model_epoch_best_4.zip -d weights/

RUN pip install -r requirements.txt

RUN pip install opencv-python==3.4.0.12

RUN python3 model.py

CMD exec gunicorn --bind :$PORT --workers 1 --threads 1 --timeout 0 app:app