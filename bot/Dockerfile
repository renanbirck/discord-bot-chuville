FROM python:3.14-alpine

RUN mkdir -p /app
WORKDIR /app

COPY *.py /app

# Versões fixas e sincronizadas com o pyproject.toml/uv.lock da raiz do
# projeto (mesmo racional do backend/Dockerfile). O pacote certo aqui é
# "python-dotenv" (fornece o módulo "dotenv" com load_dotenv()); existe um
# pacote diferente, chamado apenas "dotenv", que não é o mesmo. "requests"
# não é usado pelo bot (que fala com o backend via aiohttp).
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
        "discord-py==2.6.4" \
        "aiohttp==3.13.0" \
        "python-dotenv==1.2.2"

CMD ["python", "bot_main.py"]
