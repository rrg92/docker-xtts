FROM ghcr.io/coqui-ai/xtts-streaming-server:latest-cuda121

# Aqui é a nossa versão modificada do main.py 
# Todo o resto permance!

COPY xtts-streaming-server/server/main.py .