FROM python:3.14-alpine

RUN mkdir -p /app /data
WORKDIR /app

EXPOSE 8820

COPY *.py .

# Versões fixas e sincronizadas com o pyproject.toml/uv.lock da raiz do
# projeto: o contexto de build aqui é só backend/, então não dá pra usar o
# lockfile diretamente, mas isso evita puxar versões novas (e potencialmente
# quebradas) a cada build.
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
        "fastapi[standard]==0.139.0" \
        "sqlalchemy==2.0.51" \
        "feedparser==6.0.12" \
        "python-dotenv==1.2.2"

CMD ["fastapi", "run", "--port", "8820", "--workers", "1"]
