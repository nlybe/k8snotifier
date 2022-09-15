FROM python:3.10-alpine

RUN pip install --upgrade pip

RUN adduser -D notifier
USER notifier
WORKDIR /home/notifier
ENV PATH="/home/notifier/.local/bin:${PATH}"

COPY --chown=notifier:notifier /app .
RUN pip install --user -r requirements.txt

CMD [ "python3", "./main.py" ] 