# Standard library imports.
import random

# requests package imports.
import requests


def find_db(urls = None):

    # If an active CouchDB database is found, then this value will
    # be set to the URL value of the database.
    db = None

    # If the length of the urls is greater than zero, then continue
    # to attempt to find an active database.  Otherwise, do nothing
    # and return None.
    if len(urls) > 0:

        # Choose a random database from the given list.
        db_temp = random.choice(urls)
        db_alive = False

        try:

            r = requests.get(db_temp, timeout = 30.0)

            if r.status_code == 200:
                if r.json().get('db_name') is not None:
                    db_alive = True

        except:
            pass

        if db_alive == True:
            db = db_temp

        else:

            reduced_urls = []

            for url in urls:
                if url != db_temp:
                    reduced_urls.append(url)

            # Recursion, Yay!
            db = find_db(urls = reduced_urls)

    return

