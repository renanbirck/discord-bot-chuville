from typing import TypedDict
from datetime import datetime


class UnparsedHeadlineEntry:
    title: str
    published_parsed: tuple
    summary: str
    link: str


class Headline(TypedDict):
    post_id: int
    post_title: str
    post_date: datetime
    post_summary: str
    post_link: str
