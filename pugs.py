from pymongo import MongoClient

client = MongoClient()
db = client.makemehappy
pugs = db.pugs

pug = pugs.find_one()
print pug['url']
