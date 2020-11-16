import typing


class Book(typing.NamedTuple):
    title: str
    author: str
    description: str
    call_number: str
    cover_image: str
    full_record_link: str
