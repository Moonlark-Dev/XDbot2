FROM python:latest
WORKDIR /code
EXPOSE 8080

COPY requirements.txt requirements.txt
RUN apk add --no-cache curl build-base libressl-dev musl-dev libffi-dev &&\
  pip install --no-cache-dir --upgrade pip &&\
  pip install --no-cache-dir -r requirements.txt &&\
  pip install --no-cache-dir nonebot2[fastapi] &&\
  playwright install chromium &&\
  rm requirements.txt &&\
  rm -rf /root/.cache/pip
COPY . .
CMD ["nb", "run", "--reload"]
