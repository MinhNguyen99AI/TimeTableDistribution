# syntax=docker/dockerfile:1

FROM python:3.8.13-bullseye

WORKDIR /app
EXPOSE 5000

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt
COPY . .
#Run command in container
ENV FLASK_APP=app.py
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]