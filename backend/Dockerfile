FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./backend

ENV PORT=36301
EXPOSE 36301

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "36301"]
