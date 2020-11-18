import typing
from typing import Optional, Type, TypeVar

from ..goodreads.types import Book as GoodreadsBook

# Create a generic variable that can be 'Parent', or any subclass.
T = TypeVar('T', bound='BookDescription')


class BookDescription(typing.NamedTuple):
    """This structure contains just the data needed to query the catalog.

    It can be built from a Goodreads shelf result, since that result
    will contain some Goodreads-specific info.
    """

    # Plain ISBN, not ISBN13
    # In rare cases, it's possible for an ISBN to be missing!
    isbn: Optional[str]

    title: str
    author: str

    # NOTE: In Python 3.8 we can use `postponed evaluations of annotations`
    # to just have this method return BookQuery
    @classmethod
    def from_goodreads_book(cls: Type[T], book: GoodreadsBook) -> T:
        return cls(
            isbn=book.isbn,
            title=book.title,
            author=book.author,
        )


class Book(typing.NamedTuple):
    title: str
    author: str
    description: str
    call_number: str
    cover_image: Optional[str]
    full_record_link: Optional[str]
