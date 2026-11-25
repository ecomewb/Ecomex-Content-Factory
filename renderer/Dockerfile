# ECOMEX Folien-Renderer
# Bauen aus dem Repo-Hauptordner (der ECOMEX-Master wird mit eingebaut):
#   docker build -f renderer/Dockerfile -t ghcr.io/ecomewb/ecomex-renderer:latest .
FROM python:3.12-slim

# LibreOffice nur für die PDF-Vorschau (visuelle QA); Schriften für exakte Textvermessung
RUN apt-get update && apt-get install -y --no-install-recommends \
      libreoffice-impress fonts-open-sans fonts-dejavu-core fontconfig \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /srv
COPY renderer/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY renderer/app ./app
COPY renderer/tools ./tools
COPY renderer/config ./config
COPY renderer/masters ./masters
COPY renderer/tests/sample_deck.json ./tests/sample_deck.json
# Eigene Firmenschriften (TTF/OTF) in renderer/fonts ablegen, damit Vermessung und PDF-Vorschau exakt sind
COPY renderer/fonts /usr/local/share/fonts/ecomex

# Originalmaster einbauen – bei neuem Master: --build-arg MASTER_DATEI=design/<neue Datei>.pptx
ARG MASTER_DATEI=design/ECOMEX_Masterlayout_6.2.pptx
COPY ${MASTER_DATEI} ./masters/ecomex_master.pptx

RUN fc-cache -f && python tools/make_demo_master.py masters/demo_master.pptx \
    && useradd --system --uid 10001 --home-dir /tmp renderer && chown -R renderer /srv

ENV MASTER_PATH=/srv/masters/ecomex_master.pptx \
    CONFIG_DIR=/srv/config \
    HOME=/tmp \
    PYTHONUNBUFFERED=1
USER renderer
EXPOSE 8080
LABEL org.opencontainers.image.source="https://github.com/ecomewb/Ecomex-Content-Factory" \
      org.opencontainers.image.title="ECOMEX Folien-Renderer" \
      org.opencontainers.image.description="Setzt Deck-JSON der ECOMEX Content Factory in den ECOMEX-Folienmaster (PPTX, PDF-Vorschau, Prüfbericht, Textextraktion)"
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s \
  CMD python -c "import urllib.request;urllib.request.urlopen('http://localhost:8080/health')" || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]
