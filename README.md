# 📰 markdown-converter

![mit license](https://img.shields.io/github/license/p3t3r67x0/markdown-converter)
![github build status](https://img.shields.io/github/workflow/status/p3t3r67x0/markdown-converter/markdown-converter)
![repository size](https://img.shields.io/github/repo-size/p3t3r67x0/markdown-converter)
![python version](https://img.shields.io/github/pipenv/locked/python-version/p3t3r67x0/markdown-converter)
![docker build](https://img.shields.io/docker/cloud/build/opendatacoder/markdown)

> A tool to convert markdown with help of pandoc and LaTeX to pdf

![Write markdown and convert it to pdf](https://github.com/p3t3r67x0/markdown-converter/raw/master/docs/undraw.png)


This tool downloads all images from any online markdown repository and converts it with help of pandoc and LaTeX into a beautiful pdf. There is also an image converter integrated to convert anmimated gif or svg images into a png image. All together this tool turns text, images, links as well as emojies 🚀 into a pdf file.

You can choose to build the markdown converter or to run the docker container


## 📦 Docker Hub

Make use of the pre build docker image

```bash
docker pull opendatacoder/markdown
```


## 📦 Docker Usage

```bash
docker run --rm -v /home/ubuntu/:/app/output markdown --format md --output readme --input \
https://raw.githubusercontent.com/p3t3r67x0/markdown-converter/master/README.md
```


## 🧱 Local Docker Setup

To run the docker container have a look at **Docker Usage** section

```bash
docker build -t markdown .
```


## 🧱 Local Build Setup

```bash
# install build dependencies on debian or ubuntu
sudo apt install virtualenv python3.7 python3.7-dev \
pandoc gir1.2-rsvg-2.0 libcairo2-dev libgirepository1.0-dev \
python3-cairo python-gi-cairo python3-gi texlive-full

# create a virtualenv
virtualenv -p /usr/bin/python3.7 venv

# activate virtualenv
. venv/bin/activate

# install dependencies
pip3 install -r requirements.txt
```


## 🧱 Local Usage

Here you have a few usage examples which you can try as well on the Docker container

### 🧾 Convert markdown to LaTeX and PDF

*HINT*: You can choose between different `--format` options like `md` or `gfm` and `html`.

Fetch all assets from a remote url and convert a markdown into a **LaTeX** file and render a **pdf**.

```bash
./convert.py --format md --output readme --input \
https://raw.githubusercontent.com/p3t3r67x0/markdown-converter/master/README.md
```


### 🧾 Convert markdown to LaTeX

Use the `--dry` flag to not render a **pdf** file but convert the markdown into a **LaTeX** file with all fetched assets.

```bash
./convert.py --format md --output readme --dry --input \
https://raw.githubusercontent.com/p3t3r67x0/markdown-converter/master/README.md
```
