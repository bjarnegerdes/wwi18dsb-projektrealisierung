FROM python:3.8
COPY static static
COPY templates templates
COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY app.py app.py
CMD python -u ./app.py