FROM python:3.11.7-alpine

WORKDIR /app

ADD templates /app/templates
ADD requirements.txt /app/requirements.txt
ADD app.py /app/app.py

RUN pip install pip-tools && pip-sync

EXPOSE 8080

CMD ["python3", "app.py"]
