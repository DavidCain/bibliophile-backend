import html
import logging
import urllib.parse as urlparse
from typing import Any, Iterator, List, Optional

import grequests
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from .. import syndetics
from ..errors import UnstableAPIError
from ..goodreads.types import Book as GoodreadsBook
from .query import QueryBuilder
from .types import Book

logger = logging.getLogger('bibliophile')


class _BookPatchedResponse(requests.Response):
    """A response from the BiblioCommons catalog API, with queried book attached.

    This allows us to add metadata to a raw response object, so we know
    exactly which book was the origin of the request.
    """

    _book: Book


class BiblioParser:
    """ Use undocumented BiblioCommons APIs to extract book information. """

    def __init__(
        self,
        biblio_subdomain: str,
        branch: Optional[str] = None,
        isolanguage: Optional[str] = None,
    ):
        self.branch = branch
        self.root = f'https://{biblio_subdomain}.bibliocommons.com/'
        self.isolanguage = isolanguage

    @staticmethod
    def extract_item_id(rss_link: str) -> int:
        """Extract a numeric ID from a link to a book summary.

        'seattle.bibliocommons.com/item/show/2837203030_moby_dick' -> 2837203030

        The RSS feed for a given search links to a page with information about
        that book. The URL is a slug containing an item ID. We need that ID to
        form other requests.
        """
        path = urlparse.urlsplit(rss_link).path
        if not path.startswith('/item/show/'):
            raise UnstableAPIError("RSS link format changed!")

        slug = path.split('/')[-1]  # '2837203030_moby_dick'
        item_id = slug.split('_')[0]  # '2837203030'
        if not item_id.isdigit():
            raise UnstableAPIError("slug format changed!")
        return int(item_id)

    def _async_record(self, book: Book) -> grequests.AsyncRequest:
        """Return an asynchronous request for info about the given book.

        The response content will be the "full record," containing information
        about the given title.
        """
        assert book.full_record_link, "Record URL required to look up item!"
        item_id = self.extract_item_id(book.full_record_link)
        url = urlparse.urljoin(self.root, f'item/full_record/{item_id}')

        # See: https://requests.readthedocs.io/en/latest/user/advanced/#event-hooks
        def attach_book(
            response: _BookPatchedResponse,
            **_kwargs: Any,  # pylint:disable=unused-argument
        ) -> _BookPatchedResponse:
            """ Store the book metadata on the response object. """
            response._book = book  # pylint:disable=protected-access
            return response

        return grequests.get(url, hooks={'response': attach_book})

    def async_book_lookup(self, query: str) -> grequests.AsyncRequest:
        """Formulate & return a request that executes the query.

        The object can be asynchronously queried in a bunch with grequests.
        """
        # BiblioCommons only opens up their API to library employees
        # As of 2011, they said it would publicly-available 'soon'... =(
        rss_search = urlparse.urljoin(self.root, 'search/rss')
        params = {'custom_query': query}

        # grequests doesn't store the (full) url on AsyncRequest objects
        full_url = f"{rss_search}?{urlparse.urlencode(params)}"
        logger.debug("Searching books via RSS: '%s'", full_url)

        return grequests.get(rss_search, params=params)

    @staticmethod
    def book_from_rss_item(rss_item: Tag) -> Book:
        """ Parse out book metadata from XML in an RSS <item>. """
        # The 'description' element contains escaped HTML with <b> labels
        desc_soup = BeautifulSoup(rss_item.description.text, 'html.parser')

        # Try to get call number directly (some libraries don't have it here)
        call_num = desc_soup.find('b', text='Call #:')
        call_number = call_num.next_sibling.strip() if call_num else None

        author_label = desc_soup.find('b', text='Author:')
        author = author_label.find_next('a').text if author_label else None

        desc_label = desc_soup.find('b', text='Description:')
        description = desc_label.find_next('p').text if desc_label else ''

        # Get high-quality cover art from the thumbnail that's given for RSS
        thumbnail = desc_soup.find('div', class_="jacketCoverDiv")
        cover_image: Optional[str] = None
        if thumbnail:
            medium_gif = thumbnail.find('img').attrs['src']
            cover_image = syndetics.higher_quality_cover(image_url=medium_gif)

        return Book(
            full_record_link=rss_item.link.text,  # Can be None!
            title=html.unescape(rss_item.title.text),
            author=author,
            call_number=call_number,
            description=description,
            cover_image=cover_image,
        )

    def matching_books(self, query_response: requests.Response) -> Iterator[Book]:
        """ Yield descriptors of all books matched by the query. """
        soup = BeautifulSoup(query_response.content, 'xml')

        for tag in soup.find('channel').findAll('item'):
            yield self.book_from_rss_item(tag)

    @staticmethod
    def get_call_number(full_record_response: requests.Response) -> str:
        """ Extract a book's call number from its catalog query response. """
        # Yes, that's a JSON endpont that returns HTML. ಠ_ಠ
        soup = BeautifulSoup(full_record_response.json()['html'], 'html.parser')
        call_num = soup.find(testid="callnum_branch").find('span', class_='value')
        text: str = call_num.text
        return text

    def catalog_results(self, books: List[GoodreadsBook]) -> Iterator[Book]:
        """ Yield all books found in the catalog, in no particular order. """

        def grouper(
            # (This will work with any type - could use TypeVar if needed generically)
            input_list: List[GoodreadsBook],
            chunk_size: int,
        ) -> Iterator[List[GoodreadsBook]]:
            for i in range(0, len(input_list), chunk_size):
                yield input_list[i : i + chunk_size]

        # Undocumented, but the API appears to only support lookup of 10 books
        # (We also have a ~900 character search max to contend with)
        queries = (
            QueryBuilder.bibliocommons_query(isbn_chunk, self.branch, self.isolanguage)
            for isbn_chunk in grouper(books, 10)
        )
        lookup_requests = [self.async_book_lookup(q) for q in queries]
        for response in grequests.imap(lookup_requests):
            for book in self.matching_books(response):
                yield book

    def all_matching_books(self, books: List[GoodreadsBook]) -> Iterator[Book]:
        """ Yield all matching books for the supplied books & branch. """
        search = "Searching library catalog for books"
        if self.branch:
            search += f" at {self.branch}"
        logger.info(search)

        full_record_requests = []

        # First, yield all books with full metadata from the RSS channel
        for book in self.catalog_results(books):
            if book.call_number:
                yield book
            elif not book.full_record_link:
                logger.warning("No link given for %s, can't get call #", book.title)
            else:  # Some metadata found, but we need to more for the call #
                logger.debug("No call # found for %s, fetching record.", book.title)
                full_record_requests.append(self._async_record(book))

        # Then yield books that need additional lookups to fetch call numbers
        for response in grequests.imap(full_record_requests):
            book = response._book  # pylint: disable=protected-access
            yield book._replace(call_number=self.get_call_number(response))
