FROM python:3.8-slim-buster

ADD web_scraper.py .

RUN pip install uuid selenium 

CMD [ "python", "./main.py" ]