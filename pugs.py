from pymongo import MongoClient
import random

client = MongoClient()
db = client.makemehappy
pugs = db.pugs

rand = random.random()*pugs.count()
pug = pugs.find().limit(-1).skip(rand).next()

print pug['url']
