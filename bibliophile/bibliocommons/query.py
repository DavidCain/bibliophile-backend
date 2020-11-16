from typing import Iterable, Optional

from ..goodreads.types import Book as GoodreadsBook
from .errors import QueryError

# BiblioCommons will ignore any query over 900 characters.
# This was experimentally derived using the ASCII character set.
# I have no idea how Unicode code points are handled (or if they are handled at all)
MAX_QUERY_LENGTH = 900


class QueryBuilder:  # pylint: disable=too-few-public-methods
    """ Construct BiblioCommons catalog queries for one or more books. """

    @staticmethod
    def _single_query(book: GoodreadsBook, print_only: bool = True) -> str:
        """ Get query for one book - Use its ISBN (preferred) or title + author. """
        conditions = {}

        if book.isbn:
            conditions['identifier'] = book.isbn
        else:
            conditions['contributor'] = book.author
            conditions['title'] = book.title
            if print_only:
                conditions['formatcode'] = 'BK'

        rules = [f'{name}:({val})' for name, val in conditions.items()]
        query = ' AND '.join(rules)
        return f'({query})' if len(rules) > 1 else query

    @classmethod
    def _query(
        cls,
        books: Iterable[GoodreadsBook],
        branch: Optional[str],
        isolanguage: Optional[str],
        print_only: bool,
    ) -> str:
        """Get query for "any of these books available at this branch."

        Note that this query may not actually be accepted!
        Use the public method, `bibliocommons_query()` for validation.
        """
        isbn_match = ' OR '.join(
            cls._single_query(book, print_only=print_only) for book in books
        )
        parts = []
        if branch:
            parts.append(f'available:"{branch}"')
        if isolanguage:
            parts.append(f'isolanguage:"{isolanguage}"')

        return f'({isbn_match}) {" ".join(parts)}' if parts else isbn_match

    @classmethod
    def bibliocommons_query(
        cls,
        books: Iterable[GoodreadsBook],
        branch: Optional[str],
        isolanguage: Optional[str],
        print_only: bool = True,
    ) -> str:
        """Get query for "any of these books available [at this branch] and/or [in this language]"

        This query can be used in any Bibliocommons-driven catalog.

        If the query is invalid, an exception will be raised.
        """
        query = cls._query(
            books, branch=branch, isolanguage=isolanguage, print_only=print_only
        )

        if len(query) > MAX_QUERY_LENGTH:
            raise QueryError("BiblioCommons queries are limited to 900 chars!")
        return query
