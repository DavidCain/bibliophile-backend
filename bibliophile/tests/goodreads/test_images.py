import unittest
from unittest import mock

from bibliophile.goodreads.images import higher_quality_cover, logger


class CoverImageTests(unittest.TestCase):
    def test_nophoto_url_unchanged(self):
        """ We handle Goodreads' "nophoto" URL. """
        nophoto = (
            "https://www.goodreads.com/"
            "assets/nophoto/book/111x148-bcc042a9c91a29c1d680899eff700a03.png"
        )
        image_url = higher_quality_cover(nophoto)
        self.assertEqual(image_url, nophoto)

    def test_unrecognized_image_format(self):
        """ If the photo is not recognized, we just return it as-is. """
        unexpected_format_url = 'https://images.gr-assets.com/12345789.jpg'
        with mock.patch.object(logger, 'warning') as log_warning:
            image_url = higher_quality_cover(unexpected_format_url)
        log_warning.assert_called_once()
        self.assertEqual(image_url, unexpected_format_url)

    def test_old_photo_(self):
        # Still works, but not expected in the API
        old_format_url = 'https://images.gr-assets.com/books/1550917827s/1202.jpg'
        self.assertEqual(
            higher_quality_cover(old_format_url),
            'https://images.gr-assets.com/books/1550917827l/1202.jpg',
        )

    # This is what the API currently responds with!
    # - images hosted on CDN
    # - The full-size image is used, but with a resize applied
    def test_small_resized_cdn_photo_enlarged(self):
        self.assertEqual(
            higher_quality_cover(
                'https://i.gr-assets.com/images/S/compressed.photo.goodreads.com/books/1367778804l/17081913._SX98_.jpg'
            ),
            'https://i.gr-assets.com/images/S/compressed.photo.goodreads.com/books/1367778804l/17081913.jpg',
        )

    def test_small_raw_cdn_photo_enlarged(self):
        """ We can produce higher-quality images for a small-sized cover served from the CDN. """
        self.assertEqual(
            higher_quality_cover(
                'https://i.gr-assets.com/images/S/compressed.photo.goodreads.com/books/1367778804l/17081913.jpg'
            ),
            'https://i.gr-assets.com/images/S/compressed.photo.goodreads.com/books/1367778804l/17081913.jpg',
        )

    def test_small_base_photo_enlarged(self):
        """ We can produce higher-quality images for a small-sized cover served from the Goodreads site. """
        self.assertEqual(
            # Note that HTTP (not HTTPS) is used!
            higher_quality_cover(
                'http://compressed.photo.goodreads.com/books/1367778804s/17081913.jpg'
            ),
            'http://compressed.photo.goodreads.com/books/1367778804l/17081913.jpg',
        )
