FROM python:3.8
COPY ./ExtractInsertDB.py ./ExtractInsertDB.py
COPY ./SentimentModel.py ./SentimentModel.py
COPY ./resource /resource
COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY ./start.sh start.sh
CMD bash start.sh