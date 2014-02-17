from pymongo import MongoClient
import random
from flask import Flask, render_template
from flask_oauth import OAuth

SECRET_KEY = 'makemehappy2014'
DEBUG = True
FACEBOOK_APP_ID = '131978466977157'
FACEBOOK_APP_SECRET = 'eedce7bad71c67e1c8e47e14822edb62'

app = Flask(__name__)
app.debug = DEBUG
app.secret_key = SECRET_KEY
oauth = OAuth()

client = MongoClient()
db = client.makemehappy
pugs = db.pugs

@app.route('/')
def hello():
    return render_template('index.html')



# PUG GENERATORS

@app.route("/pugs")
def random_pugs():
    rand = int(random.random()*pugs.find({"animated": 1}).count())
    pug = pugs.find({"animated": 1}).limit(-1).skip(rand).next()
    return pug['url']

@app.route("/pugs_static")
def random_static_pugs():
    rand = int(random.random()*pugs.find({"animated": 0}).count())
    pug = pugs.find({"animated": 0}).limit(-1).skip(rand).next()
    return pug['url']

@app.route("/pugs_mixed")
def random_mixed_pugs():
    rand = int(random.random()*pugs.find().count())
    pug = pugs.find().limit(-1).skip(rand).next()
    return pug['url']

if __name__ == "__main__":
    app.run()
