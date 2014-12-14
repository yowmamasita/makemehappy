from pymongo import MongoClient
import datetime
import requests
import time
import Image
import magic

API_KEY = "&api_key=d0wby4txhKrlfdHmN7WvAy5VDEs11ltp1ZOAH8xqQBgVZYxS5S"
SEARCH_TERMS = ['pug', 'pugs', 'pug+gif', 'pug+gifs']

for tag in SEARCH_TERMS:
    # build url
    url = "http://api.tumblr.com/v2/tagged?tag=" + tag + API_KEY

    # setup db
    client = MongoClient()
    db = client.makemehappy
    pugs = db.pugs

    # try searching for tag
    try:
        r = requests.get(url)
        breaker = 5
        while r.status_code != 200 and breaker >= 0:
            breaker -= 1
            print "Request error: " + url
            time.sleep(15)
            r = requests.get(url)
    except:
        pass

    if breaker >= 0:
        data = r.json()

        # iterate over each search result
        for resp in data['response']:

            not_a_gif = 0
            _id = resp['id']

            try:
                photo = resp['photos'][0]['original_size']['url']
            except KeyError:
                continue

            try:
                # existing?
                if pugs.find_one({"$or": [{"id": _id}, {"url": photo}]}):
                    continue

                # download photo for analysis
                response = requests.get(photo, stream=True)
                breaker = 5
                while response.status_code != 200 and breaker >= 0:
                    breaker -= 1
                    print "Request error: " + photo
                    time.sleep(15)
                    response = requests.get(photo, stream=True)

            except:
                print "Request error: " + photo
                continue

            if breaker < 0:
                continue

            filepath = "tumblr.gif"

            with open(filepath, 'w') as f:

                chunk = response.iter_content(256).next()
                f.write(chunk)
                mime = magic.from_buffer(chunk, mime=True)

                if "image" not in mime:
                    # NOT A GIF
                    not_a_gif = 1
                else:
                    # continue download
                    for chunk in response.iter_content(256):
                        f.write(chunk)

            # if it is a gif, check if animated
            if not_a_gif == 0:
                animated = 0
                gif = Image.open(filepath)

                try:
                    gif.seek(1)
                except EOFError:
                    # NOT ANIMATED
                    animated = 0
                else:
                    animated = 1

                post = {
                    "id": _id,
                    "url": photo,
                    "likes": 1,
                    "animated": animated,
                    "mime": mime,
                    "date": datetime.datetime.utcnow()
                }
                pugs.insert(post)
                print post
