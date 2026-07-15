FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app

WORKDIR /app

COPY Requirements.txt .
RUN python -m pip install --upgrade \
      "pip>=26.1,<27" \
      "setuptools>=80.9,<81" \
      "wheel>=0.46.2,<0.47" \
      "jaraco.context>=6.1,<7" \
    && python -m pip install -r Requirements.txt \
    && groupadd --gid 10001 app \
    && useradd --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app

COPY --chown=10001:10001 . .
USER 10001:10001

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=15s --retries=3 \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"]

CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
