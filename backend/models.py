from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Headline(Base):
    # Modelo referente a uma manchete (headline) do feed RSS.

    __tablename__ = "RSS_Entries"
    entry_id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    entry_title: Mapped[str]
    entry_publication_date: Mapped[datetime]
    entry_summary: Mapped[str]
    entry_link: Mapped[str] = mapped_column(
        unique=True
    )  # O título pode se repetir, podem ocorrer duas notícias na mesma data
    # (comum, se o blog usa agendamento automático), mas o link tem que ser único pela própria natureza dos links
    was_already_posted: Mapped[bool] = mapped_column(default=False)
    # Quando o bot confirmou a postagem (em /mark_headline_as_read). Fica NULL
    # nas notícias postadas antes de essa coluna existir.
    posting_date: Mapped[datetime | None]
    # O último erro que o bot relatou ao tentar postar a notícia (em
    # /report_posting_error); é apagado quando a postagem enfim dá certo.
    posting_error: Mapped[str | None]
