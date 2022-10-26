FROM python:3.10.6-buster

ENV WORKING_DIR /user/app/IntelligentSocketDatalogger
WORKDIR $WORKING_DIR

COPY requirements.txt ./

RUN pip install -r requirements.txt
RUN pip install schedule
RUN pip install influxdb
RUN pip install python-dateutil

COPY files/ ./files/
COPY source/ ./source/

ENV PYTHONPATH "${PYTHONPATH}:/user/app/IntelligentSocketDatalogger"

WORKDIR /user/app/IntelligentSocketDatalogger/source/

CMD ["python", "-u", "main.py"]