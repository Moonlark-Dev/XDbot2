FROM python:latest
WORKDIR /code
EXPOSE 8080

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt &&\
  pip install nonebot2[fastapi] &&\
  playwright install chromium &&\
  playwright install-deps

COPY . .
CMD ["nb", "run", "--reload"]
