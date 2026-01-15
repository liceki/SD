FROM python:3.9-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
RUN pip install paho-mqtt pymongo
COPY . .
CMD ["python", "main_car.py"]