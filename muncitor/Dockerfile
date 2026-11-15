FROM python:3.9-slim

RUN pip install redis

COPY muncitor.py /app/muncitor.py

WORKDIR /app

CMD ["python", "-u", "muncitor.py"]