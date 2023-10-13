FROM python:3.10-alpine
RUN pip install django

ADD . /app
WORKDIR /app


CMD ["python", "manage.py", "runserver"]
