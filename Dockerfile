FROM python:2.7
ENV PYTHONUNBUFFERED 1
RUN mkdir /app
WORKDIR /app
RUN apt-get update && apt-get install -y smbclient cups libcups2-dev
RUN mv /usr/lib/cups/backend/parallel /usr/lib/cups/backend-available/ &&\
    mv /usr/lib/cups/backend/serial /usr/lib/cups/backend-available/ &&\
    mv /usr/lib/cups/backend/usb /usr/lib/cups/backend-available/ &&\
    mv /usr/lib/cups/backend/gutenprint52+usb /usr/lib/cups/backend-available/
ADD requirements.txt /app/
#ADD requirements/ /app/requirements/
RUN pip install -r requirements.txt