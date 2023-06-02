FROM python:latest
WORKDIR /code
ENV HOST "0.0.0.0"
ENV PORT 8080
EXPOSE 8080
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt &&\
  pip install nonebot2[fastapi] &&\
  playwright install
#  playwright install-deps
COPY . .
CMD ["nb", "run", "--reload"]
