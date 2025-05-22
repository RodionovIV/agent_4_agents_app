FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
      curl \
      ca-certificates \
      git \
      build-essential \
      libnss3 \
      libxss1 \
      libasound2 \
      libxtst6 \
      libgbm1 \
      libgtk-3-0 \
      libgdk-pixbuf2.0-0 \
      libgl1 \
      fonts-freefont-ttf \
      fontconfig \
      chromium \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
 && apt-get update && apt-get install -y nodejs \
 && npm install -g @mermaid-js/mermaid-cli \
 && npm cache clean --force \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

CMD ["python", "app.py"]
