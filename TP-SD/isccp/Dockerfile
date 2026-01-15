FROM python:3.9-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
RUN pip install paho-mqtt rpyc
COPY . .
CMD ["python", "main_isccp.py"]