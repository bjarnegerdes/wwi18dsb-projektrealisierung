FROM python:3.8
COPY ./databaseInsert.py ./databaseInsert.py
COPY ./redditPushshiftScraper.py ./redditPushshiftScraper.py
COPY ./scrapeTickersSynonyms.py ./scrapeTickersSynonyms.py
COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt
CMD python -u ./databaseInsert.py 