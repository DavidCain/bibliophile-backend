import unittest
from unittest import mock

import requests

from bibliophile.goodreads import images
from bibliophile.goodreads.shelf import ShelfReader
from bibliophile.goodreads.types import Book as GoodreadsBook


class ShelfTests(unittest.TestCase):
    def test_user_id_required(self):
        with self.assertRaises(ValueError):
            ShelfReader(user_id='', dev_key='123')
        with self.assertRaises(ValueError):
            ShelfReader(user_id=None, dev_key='abc')

    def test_key_required(self):
        with self.assertRaises(ValueError):
            ShelfReader(user_id='123456789', dev_key='')
        with self.assertRaises(ValueError):
            ShelfReader(user_id='123456789', dev_key=None)

    def test_wanted_books(self):
        reader = ShelfReader(
            user_id='123456789',
            dev_key='123abc456DEF000foobar9',
        )
        fake_response = mock.Mock()
        fake_response.content = b'''<?xml version="1.0" encoding="UTF-8"?>
            <GoodreadsResponse>
                <Request>
                <authentication>true</authentication>
                    <key><![CDATA[123abc456DEF000foobar9]]></key>
                <method><![CDATA[review_list]]></method>
                </Request>

                  <shelf exclusive=\'true\' id=\'136523200\' name=\'to-read\' sortable=\'false\'></shelf>

                <reviews start="1" end="1" total="1">
                    <review>
                  <id>3253694510</id>
                    <book>
                  <id type="integer">135479</id>
                  <isbn>0140285601</isbn>
                  <isbn13>9780140285604</isbn13>
                  <text_reviews_count type="integer">123450000</text_reviews_count>
                  <uri>omitted-for-test</uri>
                  <title>Cat\'s Cradle</title>
                  <title_without_series>Cat\'s Cradle</title_without_series>
                  <image_url>https://i.gr-assets.com/images/S/compressed.photo.goodreads.com/books/1327867150l/135479._SX98_.jpg</image_url>
                  <small_image_url>https://i.gr-assets.com/images/S/compressed.photo.goodreads.com/books/1327867150l/135479._SY75_.jpg</small_image_url>
                  <large_image_url/>
                  <link>https://www.goodreads.com/book/show/135479.Cat_s_Cradle</link>
                  <num_pages>0</num_pages>
                  <format>Paperback</format>
                  <edition_information/>
                  <publisher>Fake</publisher>
                  <publication_day/>
                  <publication_year>1782</publication_year>
                  <publication_month/>
                  <average_rating>3.14159</average_rating>
                  <ratings_count>123450000</ratings_count>
                  <description>Totally made up description</description>
                <authors>
                <author>
                <id>99999999</id>
                <name>Kurt Vonnegut Jr.</name>
                <role></role>
                <image_url nophoto=\'false\'>
                <![CDATA[https://images.gr-assets.com/authors/1433582280p5/2778055.jpg]]>
                </image_url>
                <small_image_url nophoto=\'false\'>
                <![CDATA[https://images.gr-assets.com/authors/1433582280p2/2778055.jpg]]>
                </small_image_url>
                <link><![CDATA[https://www.goodreads.com/author/show/2778055.Kurt_Vonnegut_Jr_]]></link>
                <average_rating>3.14159</average_rating>
                <ratings_count>123450000</ratings_count>
                <text_reviews_count>123450000</text_reviews_count>
                </author>
                </authors>
                  <published>1789</published>
                <work>  <id>1621115</id>
                  <uri>omitted-for-test</uri>
                </work></book>

                  <rating>0</rating>
                  <votes>0</votes>
                  <spoiler_flag>false</spoiler_flag>
                  <spoilers_state>none</spoilers_state>

                <shelves>

                    <shelf exclusive=\'true\' id=\'136523200\' name=\'to-read\' review_shelf_id=\'2896197272\' sortable=\'false\'></shelf>

                </shelves>

                  <recommended_for></recommended_for>
                  <recommended_by></recommended_by>
                  <started_at></started_at>
                  <read_at></read_at>
                  <date_added>Sun Mar 29 22:51:53 -0700 2020</date_added>
                  <date_updated>Sun Mar 29 22:51:53 -0700 2020</date_updated>
                  <read_count>0</read_count>
                  <body>
                  </body>

                  <comments_count>0</comments_count>
                    <url><![CDATA[https://www.goodreads.com/review/show/3253694510]]></url>
                  <link><![CDATA[https://www.goodreads.com/review/show/3253694510]]></link>
                    <owned>0</owned>
                </review>
                </reviews>

            </GoodreadsResponse>
            '''

        with mock.patch.object(requests, 'get') as requests_get:
            requests_get.return_value = fake_response
            with mock.patch.object(images, 'higher_quality_cover') as higher_quality:
                higher_quality.return_value = 'https://i.gr-assets.com/foo.jpg'
                all_books = list(reader.wanted_books(shelf='to-read'))

        higher_quality.assert_called_once_with(
            'https://i.gr-assets.com/images/S/compressed.photo.goodreads.com/books/1327867150l/135479._SX98_.jpg'
        )

        self.assertEqual(
            all_books,
            [
                GoodreadsBook(
                    isbn='0140285601',  # ISBN13: 9780140285604
                    title="Cat's Cradle",
                    author='Kurt Vonnegut Jr.',
                    description='Totally made up description',
                    image_url='https://i.gr-assets.com/foo.jpg',
                )
            ],
        )
