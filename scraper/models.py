from sqlalchemy import Boolean, Column, DateTime, Integer, String

from .database import Base


class Headline(Base):
    # Modelo referente a uma manchete (headline) do feed RSS.

    __tablename__ = "RSS_Entries"
    entry_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    entry_title = Column(String)
    entry_publication_date = Column(DateTime)
    entry_summary = Column(String)
    entry_link = Column(
        String, unique=True
    )  # O título pode se repetir, podem ocorrer duas notícias na mesma data
    # (comum, se o blog usa agendamento automático), mas o link tem que ser único pela própria natureza dos links
    was_already_posted = Column(Boolean)
