FROM python:3.9-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
RUN pip install flask pymongo
COPY . .
CMD ["python", "app.py"]