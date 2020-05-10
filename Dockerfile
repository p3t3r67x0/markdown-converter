FROM opendatacoder/latex

COPY . /home/latex/data
WORKDIR /home/latex/data

RUN apt update
RUN apt install -y gir1.2-rsvg-2.0 libcairo2-dev libgirepository1.0-dev \
  gobject-introspection python3 python3-cairo python-gi-cairo python3-gi
RUN apt clean -y

RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3", "./convert.py"]
