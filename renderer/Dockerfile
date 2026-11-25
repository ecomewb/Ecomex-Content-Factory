# ECOMEX Folien-Renderer
FROM python:3.12-slim

# LibreOffice nur für die PDF-Vorschau (visuelle QA); Schriften für exakte Textvermessung
RUN apt-get update && apt-get install -y --no-install-recommends \
      libreoffice-impress fonts-open-sans fonts-dejavu-core fontconfig \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY tools ./tools
COPY config ./config
COPY masters ./masters
# Eigene Firmenschriften (TTF/OTF) hier ablegen, damit Vermessung und PDF-Vorschau exakt sind
COPY fonts /usr/local/share/fonts/ecomex
RUN fc-cache -f && python tools/make_demo_master.py masters/demo_master.pptx

ENV MASTER_PATH=/srv/masters/ecomex_master.pptx \
    CONFIG_DIR=/srv/config \
    PYTHONUNBUFFERED=1
EXPOSE 8080
HEALTHCHECK CMD python -c "import urllib.request;urllib.request.urlopen('http://localhost:8080/health')" || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]
