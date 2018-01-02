FROM ubuntu:latest
RUN apt-get update -y
RUN apt-get install -y python3-pip python3.5 build-essential

COPY ./requirements.txt /app/requirements.txt
WORKDIR /app

RUN pip3 install -r requirements.txt
COPY ./ /app

ENTRYPOINT ["python3.5"]
CMD ["runserver.py"]