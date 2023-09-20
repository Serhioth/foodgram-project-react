FROM python:3.9
RUN apt-get update &&\
    apt-get upgrade -y
WORKDIR /app
COPY requirements.txt ./
RUN pip install -U pip &&\
    pip install -r requirements.txt --no-cache-dir
COPY . .
RUN chmod a+x run_app.sh
ENTRYPOINT ["/app/run_app.sh"]
