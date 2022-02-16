FROM python:3.8-slim-buster

ADD . .

RUN pip install -r requirements.txt

CMD [ "python", "scraper/__main__.py" ]