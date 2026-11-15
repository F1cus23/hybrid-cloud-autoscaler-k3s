FROM python:3.9-slim
WORKDIR /app
RUN pip install redis
COPY recuperator.py .
CMD ["python", "-u", "recuperator.py"]