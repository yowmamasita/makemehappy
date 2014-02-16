import praw
from pymongo import MongoClient
import datetime
import requests
import time
import Image
import magic

for sr in ['pugs', 'pug', 'Puggifs']:
    client = MongoClient()
    db = client.makemehappy
    pugs = db.pugs

    r = praw.Reddit(user_agent='pugsmakemehappy')
    # submissions = r.get_subreddit(sr).get_top_from_all(limit=None)
    submissions = r.get_subreddit(sr).get_new(limit=None)
    xx = 0
    for x in submissions:
        xx += 1
        print str(xx)+" >>> "+x.url+" ("+sr+")"
        not_a_gif = 0
        if pugs.find_one({"$or": [{"id": x.id}, {"url": x.url}]}):
            # print "Dupe: "+x.url
            continue
        else:
            try:
                response = requests.get(x.url, stream=True)
                breaker = 5
                while response.status_code != 200 and breaker >= 0:
                    breaker -= 1
                    print "Request error: "+x.url
                    time.sleep(15)
                    response = requests.get(x.url, stream=True)
            except:
                print "Request fatal error: "+x.url
                continue
            if breaker < 0:
                continue
            filepath = "/var/www/cess/makemehappy/test.gif"
            mime = "foo/bar"
            with open(filepath, 'w') as f:
                chunk = response.iter_content(256).next()
                f.write(chunk)
                mime = magic.from_buffer(chunk, mime=True)
                if "image" not in mime:
                    # print mime+" not a gif: "+x.url
                    not_a_gif = 1
                else:
                    for chunk in response.iter_content(256):
                        f.write(chunk)
            # f.close()
            if not_a_gif == 0:
                animated = 0
                gif = Image.open(filepath)
                try:
                    gif.seek(1)
                except EOFError:
                    animated = 0
                    # print "Not animated: "+x.url
                else:
                    animated = 1
                    print "Animated: "+x.url
                post = {"id": x.id,
                        "url": x.url,
                        "likes": 1,
                        "animated": animated,
                        "mime": mime,
                        "date": datetime.datetime.utcnow()}
                pugs.insert(post)
