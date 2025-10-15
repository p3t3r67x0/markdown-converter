FROM opendatacoder/latex

# Copy code first to avoid redownloading packages on every rebuild
COPY . /home/latex/data
WORKDIR /home/latex/data

# Install system dependencies for PyGObject and PyCairo
RUN apt-get update && apt-get install -y \
    gir1.2-rsvg-2.0 \
    libcairo2-dev \
    libgirepository1.0-dev \
    gobject-introspection \
    python3 \
    python3-pip \
    python3-wheel \
    python3-cairo \
    python3-gi \
    python3-gi-cairo \
    pkg-config \
    libglib2.0-dev \
 && apt-get clean -y \
 && rm -rf /var/lib/apt/lists/*

# Upgrade pip to support new metadata (like attrs 25.4.0)
RUN pip install --upgrade pip setuptools wheel

# Install your Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python3", "./convert.py"]
