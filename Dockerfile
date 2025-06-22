FROM python:3.13-slim

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

ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium \
    PUPPETEER_ARGS="--no-sandbox --disable-setuid-sandbox" \
    DANGEROUSLY_DISABLE_SANDBOX=1

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip

RUN pip install uv && uv sync

RUN git config --global --add safe.directory /app/sandbox
RUN git config --global user.email "mr.ts777@yandex.ru"
RUN git config --global user.name "RodionovIV"

CMD ["uv", "run", "app.py"]
