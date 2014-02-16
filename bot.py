import praw
from pymongo import MongoClient
import datetime

client = MongoClient()
db = client.makemehappy
pugs = db.pugs

r = praw.Reddit(user_agent='pugsmakemehappy')
submissions = r.get_subreddit('Puggifs').get_new(limit=None)
for x in submissions:
    if pugs.find_one({"id": x.id}).count() > 0:
        continue
    post = {"id": x.id,
            "url": x.url,
            "likes": 1,
            "date": datetime.datetime.utcnow()}
    pugs.insert(post)
