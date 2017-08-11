FROM ubuntu:14.04

MAINTAINER Patrycja Krawczuk <patrycja.krawczuk@mssm.edu>

RUN apt-get update && apt-get install -y python
RUN apt-get update && apt-get install -y python-pip
RUN apt-get update && apt-get install -y python-dev
RUN apt-get update && apt-get install -y python-MySQLdb

RUN pip install numpy
RUN pip install pandas
RUN pip install Flask
RUN pip install sqlalchemy
RUN pip install flask-sqlalchemy

RUN mkdir biotoolbay
COPY . /biotoolbay

ENTRYPOINT python /biotoolbay/Website/__init__.py