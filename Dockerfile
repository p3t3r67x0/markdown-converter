FROM python:3.7.3-slim

COPY . /app
WORKDIR /app

RUN apt update && apt upgrade -y && apt install -y sudo apt install pandoc texlive-full gir1.2-rsvg-2.0 libcairo2-dev libgirepository1.0-dev python3-cairo python-gi-cairo python3-gi
RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3", "./convert.py"]
