from pymongo import MongoClient
import random
from flask import Flask
app = Flask(__name__)

client = MongoClient()
db = client.makemehappy
pugs = db.pugs

@app.route("/")
def hello():
    rand = int(random.random()*pugs.count())
    pug = pugs.find().limit(-1).skip(rand).next()
    return '<img src="'+pug['url']+'">'

if __name__ == "__main__":
    app.run()
