FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

CMD uvicorn trial:app --port=8000 --host=0.0.0.0
