from pymongo import MongoClient
import random

client = MongoClient()
db = client.makemehappy
pugs = db.pugs

x = 100
while x > 0:
	rand = int(random.random()*pugs.count())
	print rand; x -= 1
pug = pugs.find().limit(-1).skip(rand).next()

print pug['url']
