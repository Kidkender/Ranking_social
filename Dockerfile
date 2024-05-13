FROM python:3.11.5

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /app/staticfiles
COPY static /app/staticfiles  
WORKDIR /app 

COPY requirements.txt /app/ 
RUN pip install --no-cache -r requirements.txt 
COPY . /app/              
