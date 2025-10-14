from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime

from bot_types import UnparsedHeadlineEntry


@dataclass
class CreateHeadline:
    title: str
    publishing_date: datetime
    summary: str
    link: str

    @classmethod
    def from_entry(cls, entry: UnparsedHeadlineEntry) -> CreateHeadline:
        from time import mktime
        from datetime import datetime

        publishing_date = datetime.fromtimestamp(mktime(entry.published_parsed))
        return cls(
            title=entry.title,
            publishing_date=publishing_date,
            summary=entry.summary,
            link=entry.link,
        )