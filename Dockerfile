FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY ddl.sql .
COPY tests/ ./tests/

RUN mkdir -p /source /target

CMD ["python", "main.py"]