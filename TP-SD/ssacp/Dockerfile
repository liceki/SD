FROM python:3.9-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
RUN pip install rpyc pymongo
COPY . .
CMD ["python", "main_server.py"]