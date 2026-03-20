FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app

WORKDIR /app

COPY requirements.txt /app/Seriema/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/Seriema/requirements.txt

COPY . /app/Seriema

EXPOSE 8000

CMD ["uvicorn", "Seriema.main:app", "--host", "0.0.0.0", "--port", "8000"]
