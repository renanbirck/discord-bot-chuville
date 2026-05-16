FROM python:3.14-alpine 

RUN mkdir -p /app 
WORKDIR /app 
RUN cd /app 

COPY *.py /app
RUN pip install --upgrade pip 
RUN pip install discord.py requests dotenv 

CMD ["python", "bot_main.py"]