import unittest
import uuid
from unittest import mock

import grequests
from bs4 import BeautifulSoup

from bibliophile.bibliocommons.parse import BiblioParser
from bibliophile.bibliocommons.types import Book as BiblioCommonsBook
from bibliophile.errors import UnstableAPIError


class ItemExtractionTest(unittest.TestCase):
    def test_extract_item_id(self):
        self.assertEqual(
            BiblioParser.extract_item_id(
                'https://seattle.bibliocommons.com/item/show/2837203030_moby_dick',
            ),
            2837203030,
        )

    def test_unstable_link_format(self):
        with self.assertRaises(UnstableAPIError):
            BiblioParser.extract_item_id(
                'https://seattle.bibliocommons.com/item/2837203030_moby_dick',
            )

    def test_unstable_slug_format(self):
        with self.assertRaises(UnstableAPIError):
            BiblioParser.extract_item_id(
                f'https://seattle.bibliocommons.com/item/show/{uuid.uuid4()}'
            )

        with self.assertRaises(UnstableAPIError):
            BiblioParser.extract_item_id(
                'https://seattle.bibliocommons.com/item/show/123/not_expected'
            )


class BookFromRSSTest(unittest.TestCase):
    def test_book_from_rss_item(self):
        rss_item_xml = '''
            <item>
            <title>The Future of the Internet and How to Stop It</title>
            <link>https://sfpl.bibliocommons.com/item/show/2156713093_the_future_of_the_internet_and_how_to_stop_it</link>
            <description>&lt;b&gt;Title:&lt;/b&gt; The Future of the Internet and How to Stop It&lt;br/&gt;
            &lt;b&gt;Author:&lt;/b&gt; &lt;a href="https://sfpl.bibliocommons.com/search?q=%22Zittrain%2C+Jonathan%22&amp;amp;search_category=author&amp;amp;t=author" target="_parent" testid="author_search"&gt;Zittrain, Jonathan&lt;/a&gt;&lt;br/&gt;
            &lt;b&gt;Imprint:&lt;/b&gt; New Haven [Conn.] : &lt;span class="publisher"&gt;Yale University Press&lt;/span&gt;&lt;br/&gt;
            &lt;b&gt;Call #:&lt;/b&gt; 004.678 Z695f&lt;br/&gt;
            &lt;b&gt;Format:&lt;/b&gt; Book&lt;br/&gt;
            &lt;b&gt;Series:&lt;/b&gt; &lt;br/&gt;
            &lt;b&gt;Description:&lt;/b&gt; &lt;p&gt;&lt;/p&gt;&lt;br/&gt;
                            &lt;div class='jacketCoverDiv'&gt;&lt;img alt="The Future of the Internet and How to Stop It" class="jacketCover medium" data-js="" fallback="//cor-cdn-static.bibliocommons.com/assets/default_covers/icon-book-93409e4decdf10c55296c91a97ac2653.png" id="2156713093" src="https://secure.syndetics.com/index.aspx?isbn=9780300124873/SC.GIF&amp;amp;client=sfpl&amp;amp;type=xw12&amp;amp;oclc=" title="The Future of the Internet and How to Stop It" /&gt;&lt;/div&gt;
            &lt;br/&gt;
            &lt;a href="https://sfpl.bibliocommons.com/item/show/2156713093_the_future_of_the_internet_and_how_to_stop_it"&gt;Read More&lt;/a&gt;
            </description>
            <pubDate>Mon, 30 Jun 2008 14:17:00 -0400</pubDate>
            <dc:date>2008-06-30T14:17:00-04:00</dc:date>
            </item>
        '''
        rss_item = BeautifulSoup(rss_item_xml, 'xml').find('item')
        self.assertEqual(
            BiblioParser.book_from_rss_item(rss_item),
            BiblioCommonsBook(
                full_record_link='https://sfpl.bibliocommons.com/item/show/2156713093_the_future_of_the_internet_and_how_to_stop_it',
                title='The Future of the Internet and How to Stop It',
                author='Zittrain, Jonathan',
                call_number='004.678 Z695f',
                description='',
                cover_image='https://secure.syndetics.com/index.aspx?isbn=9780300124873%2FLC.jpg&client=sfpl&type=xw12',
            ),
        )


# TODO: Lots more coverage needed here.
class BiblioParserTest(unittest.TestCase):
    def test_async_book_lookup(self):
        parser = BiblioParser(biblio_subdomain='sfpl')
        fake_request = mock.Mock(spec=grequests.AsyncRequest)
        with mock.patch.object(grequests, 'get') as grequests_get:
            grequests_get.return_value = fake_request
            ret = parser.async_book_lookup(query='(identifier:(0142437239)')
        self.assertEqual(ret, fake_request)
        grequests_get.assert_called_once_with(
            'https://sfpl.bibliocommons.com/search/rss',
            params={'custom_query': '(identifier:(0142437239)'},
        )

    def test_no_books(self):
        parser = BiblioParser(
            biblio_subdomain='sfpl',
            branch='MAIN',
            isolanguage='eng',
        )
        self.assertEqual(list(parser.all_matching_books([])), [])
