FROM python:3.8-slim-buster

ADD web_scraper.py .

RUN pip install -r requirements.txt

CMD [ "python", "./main.py" ]