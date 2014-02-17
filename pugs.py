from pymongo import MongoClient
import random
from flask import Flask, render_template, url_for
app = Flask(__name__)

client = MongoClient()
db = client.makemehappy
pugs = db.pugs

@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/css')
def css():
    return url_for('static', filename='css/bootstrap.min.css')

@app.route("/pugs")
def random_pugs():
    rand = int(random.random()*pugs.find({"animated": 1}).count())
    pug = pugs.find({"animated": 1}).limit(-1).skip(rand).next()
    return pug['url']

if __name__ == "__main__":
    app.run()
