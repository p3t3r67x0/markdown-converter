# markdown-converter

> A tool to convert markdown with help of pandoc to pdf


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

## Example

```bash
./convert.py --input https://raw.githubusercontent.com/p3t3r67x0/markdown-converter/master/README.md --format md --output readme
```
