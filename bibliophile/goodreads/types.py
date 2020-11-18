import typing
from typing import Optional


class Book(typing.NamedTuple):
    # Every Goodreads book has a slug, a string of integers which identify it.
    goodreads_id: str

    # Plain ISBN, not ISBN13
    # In rare cases, it's possible for an ISBN to be missing!
    isbn: Optional[str]

    title: str
    author: str
    description: str

    # If one exists, a book cover image
    # If no image exists, this will be a "nophoto" URL ('/assets/nophoto...')
    image_url: str
