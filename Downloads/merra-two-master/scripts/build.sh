#!/bin/sh
docker build -t merra-two:latest ./
docker stop merra-two
docker rm merra-two
docker run -v /home/ubuntu/upload/log:/app/log -p3306:3306  --detach --name merra-two merra-two:latest
docker image prune --force