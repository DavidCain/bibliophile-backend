"""
Retrieve books on a Goodreads user's "shelf."

Author: David Cain

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import logging
import urllib.parse as urlparse

import requests
from bs4 import BeautifulSoup

from .images import higher_quality_cover
from .types import Book

logger = logging.getLogger('bibliophile')


class ShelfReader:
    """ Read books from a given user's Goodreads shelves. """

    def __init__(self, user_id, dev_key):
        self.user_id = user_id
        self.dev_key = dev_key

    @staticmethod
    def get(path, params: Dict[str, Union[str, int]]):
        """ Return BS tag for the response to a given Goodreads API route. """
        endpoint = urlparse.urljoin('https://www.goodreads.com/', path)
        resp = requests.get(endpoint, params=params)
        return BeautifulSoup(resp.content, 'xml').find('GoodreadsResponse')

    def wanted_books(self, shelf):
        """ All books that the user wants to read. """
        # See: https://www.goodreads.com/api/index#reviews.list
        logger.info("Fetch books on %s for user %s", shelf, self.user_id)
        body = self.get(
            'review/list',
            {
                'v': 2,
                'id': self.user_id,
                'shelf': shelf,
                'key': self.dev_key,
                'per_page': 200,  # TODO: Paginate if more than 200 books.
            },
        )

        for review in body.find('reviews').findAll('review'):
            yield Book(
                isbn=review.isbn.text,  # Can be blank! e.g. in e-Books
                title=review.title.text,
                author=review.author.find('name').text,
                description=review.description.text,
                image_url=higher_quality_cover(review.image_url.text),
            )
