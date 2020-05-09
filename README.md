# markdown-converter

> A tool to convert markdown with help of pandoc and LaTeX to pdf

![Write markdown and convert it to pdf](./docs/undraw.png)

You can choose to build the markdown converter or to run the docker container


## Build Setup

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


## Docker Setup

```bash
docker build -t markdown .
docker run --rm -it --entrypoint /bin/bash markdown
```

## Examples

### Convert markdown to LaTeX and PDF

*HINT*: You can choose between different `--format` options like `md` or `gfm` and `html`.

Fetch all assets from a remote url and convert a markdown into a **LaTeX** file and render a **pdf**.

```bash
./convert.py --format md --output readme --input \
https://raw.githubusercontent.com/p3t3r67x0/markdown-converter/master/README.md
```


### Convert markdown to LaTeX

Use the `--dry` flag to not render a **pdf** file but convert the markdown into a **LaTeX** file with all fetched assets.

```bash
./convert.py --format md --output readme --dry --input \
https://raw.githubusercontent.com/p3t3r67x0/markdown-converter/master/README.md
```
