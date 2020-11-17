import typing
from typing import Optional


class Book(typing.NamedTuple):
    title: str
    author: str
    description: str
    call_number: str
    cover_image: Optional[str]
    full_record_link: Optional[str]
