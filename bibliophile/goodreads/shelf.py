"""
Retrieve books on a Goodreads user's "shelf."
"""

import logging
import urllib.parse as urlparse
from typing import Dict, Iterator, Union

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from . import images
from .types import Book

logger = logging.getLogger('bibliophile')


# Max number of pages which can be read at a time
# See: https://www.goodreads.com/api/index#reviews.list
PER_PAGE: int = 200


class ShelfReader:  # pylint: disable=too-few-public-methods
    """ Read books from a given user's Goodreads shelves. """

    def __init__(self, user_id: str, dev_key: str):
        if not user_id:
            raise ValueError("User ID required!")
        self.user_id = user_id

        if not dev_key:
            raise ValueError("Dev key required!")
        self.dev_key = dev_key

    @staticmethod
    def _get(path: str, params: Dict[str, Union[str, int]]) -> Tag:
        """ Return BS tag for the response to a given Goodreads API route. """
        endpoint = urlparse.urljoin('https://www.goodreads.com/', path)
        resp = requests.get(endpoint, params=params)
        return BeautifulSoup(resp.content, 'xml').find('GoodreadsResponse')

    def wanted_books(self, shelf: str) -> Iterator[Book]:
        """ All books that the user wants to read. """
        # See: https://www.goodreads.com/api/index#reviews.list
        logger.info("Fetch books on %s for user %s", shelf, self.user_id)
        body = self._get(
            'review/list',
            {
                'v': 2,
                'id': self.user_id,
                'shelf': shelf,
                'key': self.dev_key,
                # TODO: Paginate for shelves over 200 books
                # For now, we only take the top 200...
                'per_page': PER_PAGE,
            },
        )

        for review in body.find('reviews').findAll('review'):
            yield Book(
                isbn=review.isbn.text,  # Can be blank! e.g. in e-Books
                title=review.title.text,
                author=review.author.find('name').text,
                description=review.description.text,
                image_url=images.higher_quality_cover(review.image_url.text),
            )
