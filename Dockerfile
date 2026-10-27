FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && useradd --create-home --uid 10001 nutshell

COPY --chown=nutshell:nutshell . .
RUN mkdir -p /app/media && chown nutshell:nutshell /app/media

USER nutshell
EXPOSE 8000
CMD ["sh", "docker/start.sh"]
