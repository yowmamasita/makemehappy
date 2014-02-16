import praw
from pymongo import MongoClient
import datetime
import requests
import time
import Image
import magic

client = MongoClient()
db = client.makemehappy
pugs = db.pugs

r = praw.Reddit(user_agent='pugsmakemehappy')
submissions = r.get_subreddit('Puggifs').get_new(limit=None)
for x in submissions:
    not_a_gif = False
    if pugs.find_one({"$or": [{"id": x.id}, {"url": x.url}]}):
        print "Dupe: "+x.url
        continue
    else:
        response = requests.get(x.url, stream=True)
        while response.status_code != 200:
            print "Request error: "+x.url
            time.sleep(15)
            response = requests.get(x.url, stream=True)
        filepath = "/var/www/cess/makemehappy/test.gif"
        with open(filepath, 'w') as f:
            mime = magic.from_buffer(response.iter_content(256).next(), mime=True)
            if mime != "image/gif":
                print mime+" not a gif: "+x.url
                not_a_gif = True
            for chunk in response.iter_content(256):
                f.write(chunk)
        # f.close()
        if not_a_gif == False:
            gif = Image.open(filepath)
            try:
                gif.seek(1)
            except EOFError:
                print "Not animated: "+x.url
                post = {"id": x.id,
                        "url": x.url,
                        "likes": 1,
                        "animated": 0,
                        "date": datetime.datetime.utcnow()}
            else:
                print "Animated: "+x.url
                post = {"id": x.id,
                        "url": x.url,
                        "likes": 1,
                        "animated": 1,
                        "date": datetime.datetime.utcnow()}
                pugs.insert(post)
