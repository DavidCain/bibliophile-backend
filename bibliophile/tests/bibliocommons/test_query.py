import unittest

from bibliophile.bibliocommons.errors import QueryError
from bibliophile.bibliocommons.query import QueryBuilder
from bibliophile.goodreads import Book as GoodreadsBook

don_quixote = GoodreadsBook(
    goodreads_id="3836",
    isbn="0142437239",
    title="Don Quixote",
    author="Miguel de Cervantes",
    description="Windmills, Sancho Panza, etc.",
    image_url="not relevant, so not a real URL",
)

moby_dick = GoodreadsBook(
    goodreads_id="153747",
    isbn=None,  # It *does* have an ISBN, but we're pretending...
    title="Moby Dick",
    author="Herman Melville",
    description="Ahab just can't let it go",
    image_url="not relevant, so not a real URL",
)


class QueryBuilderTest(unittest.TestCase):
    def test_single_isbn(self):
        self.assertEqual(
            QueryBuilder.bibliocommons_query(
                books=[don_quixote], branch=None, isolanguage=None
            ),
            'identifier:(0142437239)',
        )

    def test_no_known_isbn(self):
        self.assertEqual(
            QueryBuilder.bibliocommons_query(
                books=[moby_dick], branch=None, isolanguage=None
            ),
            '(contributor:(Herman Melville) AND title:(Moby Dick) AND formatcode:(BK))',
        )

    def test_single_book_with_branch(self):
        self.assertEqual(
            QueryBuilder.bibliocommons_query(
                books=[don_quixote], branch='Fremont Branch', isolanguage=None
            ),
            '(identifier:(0142437239)) available:"Fremont Branch"',
        )

    def test_single_book_with_branch_and_language(self):
        self.assertEqual(
            QueryBuilder.bibliocommons_query(
                books=[don_quixote], branch='Fremont Branch', isolanguage='eng'
            ),
            '(identifier:(0142437239)) available:"Fremont Branch" isolanguage:"eng"',
        )

    def test_two_books(self):
        self.assertEqual(
            QueryBuilder.bibliocommons_query(
                books=[don_quixote, moby_dick],
                branch='Fremont Branch',
                isolanguage='eng',
            ),
            (
                # Don Quixote has an ISBN
                '(identifier:(0142437239)'
                ' OR '
                # Moby Dick has no ISBN - so we look for title, Author, book type
                '(contributor:(Herman Melville) AND title:(Moby Dick) AND formatcode:(BK)))'
                # Both books are queried as in English and at the Fremont Branch
                ' available:"Fremont Branch" isolanguage:"eng"'
            ),
        )

    def test_no_book_options_okay(self):
        self.assertEqual(
            QueryBuilder.bibliocommons_query(
                books=[moby_dick], branch=None, isolanguage=None, print_only=False
            ),
            '(contributor:(Herman Melville) AND title:(Moby Dick))',
        )

    def test_query_way_too_long(self):
        """ A query is only valid when it is below 900 characters. """
        lots_of_books = [
            GoodreadsBook(
                goodreads_id="123456",
                isbn=f"0000000{i:03d}",
                title="Unknown",
                author="Unknown",
                description="This won't be used in the query",
                image_url="not relevant, so not a real URL",
            )
            for i in range(50)
        ]

        # It's valid to query for a small number of books
        QueryBuilder.bibliocommons_query(
            books=lots_of_books[:10], branch=None, isolanguage=None
        )
        # Querying for too many introduces an exception
        with self.assertRaises(QueryError):
            QueryBuilder.bibliocommons_query(
                books=lots_of_books, branch=None, isolanguage=None
            )
