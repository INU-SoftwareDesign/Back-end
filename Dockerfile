# backend/Dockerfile

FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/
COPY .env /app/.env 
# 환경 변수 파일 EC2 내부에 이식하였음.

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "config.wsgi:application"]

