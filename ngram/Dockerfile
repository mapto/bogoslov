FROM python:3-slim-buster
RUN adduser app
WORKDIR /home/app
COPY requirements.txt .

COPY *.py .

# RUN chmod +x app.py
USER app
RUN pip install --no-cache-dir --no-warn-script-location -r requirements.txt

CMD ./app.py

# CMD tail -f /dev/null
