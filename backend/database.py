import logging

from sqlalchemy import Engine, create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.schema import CreateColumn

from .config import DATABASE_PATH

logger = logging.getLogger(__name__)

# O main.py já loga DATABASE_PATH uma única vez na inicialização; não repetimos
# o mesmo dado aqui (antes, get_db() logava a URL do banco em toda requisição).
DATABASE_URL = "sqlite:///" + DATABASE_PATH

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False, "timeout": 15})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base declarativa (estilo SQLAlchemy 2.0) para os modelos do app."""


def add_missing_columns(bind: Engine):
    """Cria nas tabelas já existentes as colunas que os modelos ganharam depois.

    O create_all() só cria as tabelas que ainda não existem; ele não mexe numa
    tabela criada por uma versão anterior do backend (como a do BD de produção),
    então faltariam nela as colunas novas e toda consulta falharia com "no such
    column". Só serve para colunas simples que aceitam NULL, que é o valor que
    elas recebem nas linhas já existentes (índices e restrições como unique não
    são criados aqui).
    """
    with bind.begin() as connection:
        inspector = inspect(connection)
        for table in Base.metadata.sorted_tables:
            existing_columns = {
                column["name"] for column in inspector.get_columns(table.name)
            }
            for column in table.columns:
                if column.name in existing_columns:
                    continue

                logger.info(
                    "Criando a coluna %s na tabela %s.", column.name, table.name
                )
                table_name = bind.dialect.identifier_preparer.format_table(table)
                column_spec = CreateColumn(column).compile(dialect=bind.dialect)
                connection.execute(
                    text(f"ALTER TABLE {table_name} ADD COLUMN {column_spec}")
                )


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
