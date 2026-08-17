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
