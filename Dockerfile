# syntax=docker/dockerfile:1

FROM python:3.11-slim AS builder

WORKDIR /build

COPY requirements.txt ./
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.11-slim AS runner

RUN addgroup --system app && adduser --system --ingroup app --home /app app

COPY --from=builder /install /usr/local
COPY --chown=app:app . /app

WORKDIR /app
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1

USER app

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--preload", "app:app"]
