FROM python:3-slim-buster

EXPOSE 8000

RUN adduser app
WORKDIR /home/app
USER app

COPY requirements.txt .

RUN pip install --no-cache-dir --no-warn-script-location -r requirements.txt

COPY *.py .

CMD ["tail", "-f", "/dev/null"]
