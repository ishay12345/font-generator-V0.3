
FROM python:3.10-slim


ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=backend/server.py
ENV FLASK_ENV=production


WORKDIR /app


RUN apt-get update && apt-get install -y \
    fontforge \
    libfreetype6-dev \
    libpng-dev \
    libjpeg-dev \
    zlib1g-dev \
    libopencv-dev \
    python3-opencv \
    libxml2-dev \
    libspiro-dev \
    libuninameslist-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


COPY backend/requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt


COPY . .


RUN mkdir -p /app/backend/uploads \
    /app/backend/split_letters_output \
    /app/backend/bw_letters \
    /app/backend/svg_letters \
    /app/backend/fonts


EXPOSE 5000


RUN pip install gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "backend.server:app"]
