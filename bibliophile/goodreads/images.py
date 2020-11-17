import logging
import re
import urllib.parse as urlparse

logger = logging.getLogger('bibliophile')

# Expect image urls to conform to a certain scheme
GOODREADS_IMAGE_REGEX = re.compile(
    # Base URL could be any of:
    # - 'https://i.gr-assets.com/images/S/compressed.photo.goodreads.com/books/(...)'
    # - 'https://images.gr-assets.com/books/(...)'
    # - 'http://compressed.photo.goodreads.com/books/(...)'
    r'/(?P<base>(images/S/compressed\.photo\.goodreads\.com/books|books))/'
    r'(?P<numeric>\d+)'  # Some numeric ID that doesn't seem to be ISBN...
    r'(?P<size>[sml])/'  # size: 'small', 'medium', or 'large'
    r'(?P<slug>\d+)'  # slug (identifier on the book's home page)
    r'((?P<resize>\._S(?P<dimension>[XY]\d+)_))?'  # optional resize (e.g. '17081913._SX98_' is 98 pixels wide)
    r'\.(?P<extension>jpg)$'
)


def higher_quality_cover(image_url: str) -> str:
    """ Modify a book cover to be higher quality. """
    parsed = urlparse.urlparse(image_url)
    if parsed.path.startswith('/assets/nophoto'):
        # No known cover for this book! Just return the "no photo" image
        return image_url

    match = GOODREADS_IMAGE_REGEX.match(parsed.path)
    if not match:
        logger.warning(
            "Goodreads image format changed! (%s) " "Returning original quality image.",
            image_url,
        )
        return image_url

    # The new path excludes:
    # - the resize group (which means we'll render full size)
    # - the original size (we'll use large automatically)
    larger_path = "/{base}/{numeric}l/{slug}.{extension}".format_map(match.groupdict())

    # Make sure to keep the original domain
    return parsed._replace(path=larger_path).geturl()
