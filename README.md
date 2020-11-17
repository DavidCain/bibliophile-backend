[![Build Status](https://travis-ci.com/DavidCain/bibliophile-backend.svg?branch=master)](https://travis-ci.com/DavidCain/bibliophile-backend)
[![Code Coverage](https://codecov.io/gh/DavidCain/bibliophile-backend/branch/master/graph/badge.svg)](https://codecov.io/gh/DavidCain/bibliophile-backend)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

# Bibliophile backend
This is a Python-based tool for finding books at the local library.

It parses your "to read" list from Goodreads.com and checks which items
are available at a library of your choosing.

## Looking for a GUI?
This repository is all you need to use the tool locally via the command line.
For a web-based user interface, see [Bibliophile][bibliophile-repo].

# Can I use this?
If you live near one of the ~190 public libraries using the BiblioCommons
system, then running this software should work for you. It relies on
undocumented APIs, so your mileage may vary.

1. Apply for a [Goodreads Developer Key][goodreads-api].
2. Obtain your Goodreads user id
3. [Optional] Set both these values in your `.bashrc`

    ```sh
    export GOODREADS_USER_ID=123456789
    export GOODREADS_DEV_KEY=whatever-your-actual-key-is
    ```
4. [Install Poetry][poetry-install]
5. Run the script!

    ```sh
    make  # One-time setup of dependencies
    ./lookup.py --biblio seattle  # Set to your own city!
    ```

Make sure you adhere to the terms of [Goodreads' API][goodreads-api-terms], and
have fun.

## Other options
You can choose to show only titles available at your local branch, select titles
from another Goodreads shelf, etc. Pass `--help` to see all options:

```
usage: lookup.py [-h] [--branch BRANCH] [--shelf SHELF] [--biblio BIBLIO]
                 [--csv CSV]
                 [user_id] [dev_key]

See which books you want to read are available at your local library.

positional arguments:
  user_id          User's ID on Goodreads
  dev_key          Goodreads developer key. See https://www.goodreads.com/api

optional arguments:
  -h, --help       show this help message and exit
  --branch BRANCH  Only show titles available at this branch. e.g. 'Fremont
                   Branch'
  --shelf SHELF    Name of the shelf containing desired books
  --biblio BIBLIO  subdomain of bibliocommons.com (seattle, vpl, etc.)
  --csv CSV        Output results to a CSV of this name.
```

## Cloud-based deployment
This may also be deployed as Lambda functions in AWS.
See the [Bibliophile README][bibliophile-repo] for instructions.


[bibliophile-repo]: https://github.com/DavidCain/bibliophile
[goodreads-api]: https://www.goodreads.com/api
[goodreads-api-terms]: https://www.goodreads.com/api/terms
[poetry-install]: https://python-poetry.org/docs/#installation
