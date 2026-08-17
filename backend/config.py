# config.py: carrega e valida as variáveis de ambiente na inicialização.
# Se algo obrigatório estiver faltando, é melhor falhar já na importação
# do que subir a API em um estado quebrado.

import sys
from os import environ

from dotenv import load_dotenv

load_dotenv()

_missing = [name for name in ("RSS_URL", "DATABASE_PATH") if name not in environ]
if _missing:
    sys.exit(
        "Faltam variáveis de ambiente: "
        + ", ".join(_missing)
        + ". Configure-as no arquivo .env (leia o README.md)."
    )

RSS_URL = environ["RSS_URL"]
DATABASE_PATH = environ["DATABASE_PATH"]
