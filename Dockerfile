FROM python:3.9.1

ADD . /app

WORKDIR /app

RUN pip install -r requirements.txt
CMD ["python", "monitor.py"]
EXPOSE 8084/tcp