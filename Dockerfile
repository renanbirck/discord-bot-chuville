FROM python:3.13-alpine

# Copiar os arquivos da aplicação
RUN mkdir -p /app /data
WORKDIR /app
RUN cd /app

COPY *.py .

# Montar o ambiente
RUN pip install --upgrade pip
RUN pip install feedparser discord.py

CMD ["python", "bot.py"]