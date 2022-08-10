FROM python:3.10.6-buster

ENV WORKING_DIR /user/app
WORKDIR $WORKING_DIR

COPY requirements.txt ./IntelligentSocketDatalogger/

RUN pip install -r ./IntelligentSocketDatalogger/requirements.txt
RUN pip install schedule
RUN pip install influxdb

COPY files/ ./IntelligentSocketDatalogger/files/
COPY source/ ./IntelligentSocketDatalogger/source/

WORKDIR /user/app/IntelligentSocketDatalogger/source

CMD ["python", "-u", "main.py"]