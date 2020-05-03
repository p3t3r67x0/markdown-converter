FROM python:3.7.3-slim

COPY . /app
WORKDIR /app

RUN apt update && apt upgrade -y && apt install -y libcairo2-dev libgirepository1.0-dev pandoc texlive-latex-recommended texlive-pictures texlive-latex-extra texlive-xetex texlive-fonts-recommended texlive-generic-recommended
RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3", "./convert.py"]
