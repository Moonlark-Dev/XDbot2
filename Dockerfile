FROM python:latest
WORKDIR /code
EXPOSE 8080

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade pip &&\
  pip install --no-cache-dir -r requirements.txt &&\
  pip install --no-cache-dir nonebot2[fastapi] &&\
  playwright install chromium &&\
  rm requirements.txt &&\
  rm -rf /root/.cache/pip
COPY . .
CMD ["nb", "run", "--reload"]
