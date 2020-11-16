import logging
import re
import urllib.parse as urlparse

logger = logging.getLogger('bibliophile')

# Expect image urls to conform to a certain scheme
GOODREADS_IMAGE_REGEX = re.compile(
    r'^/books/'
    r'(?P<slug>\d*)(?P<size>[sml])/'  # size: 'small', 'medium', or 'large'
    r'(?P<isbn>\d*).jpg$'
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
            parsed.path,
        )
        return image_url
    larger_path = f"/books/{match.group('slug')}l/{match.group('isbn')}.jpg"
    return parsed._replace(path=larger_path).geturl()
