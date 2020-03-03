FROM python:3-alpine
WORKDIR /opt/dorado_exporter/
COPY dorado_exporter.py dorado_exporter.py
COPY dorado_gather.py dorado_gather.py
COPY config.ini config.ini
COPY requirements.txt requirements.txt
RUN chmod +x dorado_exporter.py && pip install -r requirements.txt
ENTRYPOINT [ "/opt/dorado_exporter/dorado_exporter.py" ]
