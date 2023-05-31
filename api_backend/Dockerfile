# Use the official Python base image
FROM python:3.9-slim
WORKDIR /home/app/
RUN mkdir logs/
COPY requirements.txt .
RUN apt-get update && apt-get install -y default-libmysqlclient-dev build-essential
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "main.py"]
