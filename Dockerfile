FROM opendatacoder/latex

COPY . /home/latex/data
WORKDIR /home/latex/data

RUN apt update
RUN apt install -y gir1.2-rsvg-2.0 libcairo2-dev libgirepository1.0-dev \
  gobject-introspection python3 python3-pip python3-wheel python3-cairo \
  python3-gi python3-gi-cairo
RUN apt clean -y

RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3", "./convert.py"]
