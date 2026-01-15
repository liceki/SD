FROM python:3.9-slim
WORKDIR /app


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY . .

# O comando padrão será sobrescrito pelo docker-compose
CMD ["python", "server.py"]