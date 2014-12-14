from pymongo import MongoClient
import datetime
import requests
import time
import Image
import magic
import praw

SUBREDDITS = ['pugs', 'pug', 'Puggifs']

# setup db
client = MongoClient()
db = client.makemehappy
pugs = db.pugs

for subreddit in SUBREDDITS:

    r = praw.Reddit(user_agent='pugs.makemehappy')
    submissions = r.get_subreddit(subreddit).get_new(limit=None)
    # submissions = r.get_subreddit(subreddit).get_top_from_all(limit=None)

    for index, submission in enumerate(submissions, start=1):

        not_a_gif = 0
        # existing?
        if pugs.find_one({"$or": [{"id": submission.id}, {"url": submission.url}]}):
            continue

        else:
            try:
                # download photo for analysis
                response = requests.get(submission.url, stream=True)
                breaker = 5
                while response.status_code != 200 and breaker >= 0:
                    breaker -= 1
                    print "Request error:", submission.url
                    time.sleep(15)
                    response = requests.get(submission.url, stream=True)

            except:
                print "Request error:", submission.url
                continue

            if breaker < 0:
                continue

            filepath = "reddit.gif"

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
                    "id": submission.id,
                    "url": submission.url,
                    "likes": 1,
                    "animated": animated,
                    "mime": mime,
                    "date": datetime.datetime.utcnow()
                }
                pugs.insert(post)
                print post
