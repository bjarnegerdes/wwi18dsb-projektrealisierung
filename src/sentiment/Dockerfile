FROM python:3.8
COPY ./ExtractInsertDB.py ./ExtractInsertDB.py
COPY ./SentimentModel.py ./SentimentModel.py
COPY ./resource /resource
COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install /resource/en_core_web_sm-3.0.0.tar.gz
CMD python -u ./ExtractInsertDB.py