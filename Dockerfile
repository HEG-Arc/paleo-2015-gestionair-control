FROM python:2.7
ENV PYTHONUNBUFFERED 1
RUN mkdir /app
WORKDIR /app
ADD requirements.txt /app/
#ADD requirements/ /app/requirements/
RUN pip install -r requirements.txt