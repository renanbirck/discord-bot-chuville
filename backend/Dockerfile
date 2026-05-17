FROM python:3.13-alpine

RUN mkdir -p /app /data
WORKDIR /app

EXPOSE 8820

COPY *.py .

RUN pip install --upgrade pip
RUN pip install fastapi sqlalchemy fastapi[standard] feedparser python-dotenv
CMD ["fastapi", "run", "--port", "8820","--workers", "1"]
