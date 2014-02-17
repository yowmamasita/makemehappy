from pymongo import MongoClient
import random
from flask import Flask, render_template, url_for, session, request, redirect, jsonify
from flask_oauth import OAuth
import datetime

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
likes = db.likes
users = db.users

facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=FACEBOOK_APP_ID,
    consumer_secret=FACEBOOK_APP_SECRET,
    request_token_params={'scope': 'email'}
)

@app.route('/')
def hello():
    f_id = None
    name = None
    if session.get('oauth_token'):
        me = facebook.get('/me')
        f_id = me.data['id']
        name = me.data['name']
    return render_template('index.html', f_id=f_id, name=name)

@app.route('/login')
def login():
    return facebook.authorize(callback='http://arch.cessallapitan.me/makemehappy/login/authorized')

@app.route('/logout')
def logout():
    session.pop('oauth_token', None)
    return redirect(url_for('hello', _external=True))

@app.route('/login/authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['oauth_token'] = (resp['access_token'], '')
    return redirect(url_for('hello', _external=True))

@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

@app.route('/pug/')
@app.route('/pug/<pug_id>')
def that_pug(pug_id=None):
    if pug_id is None:
        return redirect(url_for('hello', _external=True))
    if is_number(pug_id):
        pug = pugs.find_one({"id": int(pug_id)})
        pug['id'] = str(pug['id'])
    else:
        pug = pugs.find_one({"id": pug_id})
    return render_template('pug.html', pug=pug)

@app.route('/like/')
@app.route('/like/<pug_id>')
def like_pug(pug_id=None):
    if pug_id is None:
        return jsonify({'msg':'error', 'error':'pug_id missing'})
    if session.get('oauth_token'):
        me = facebook.get('/me')
        f_id = me.data['id']
        name = me.data['name']
        like = likes.find_one({"$and":[{"pug_id": str(pug_id)}, {"f_id": str(f_id)}]})
        if like:
            return jsonify({'msg':'error', 'error':'you liked this already'})
        else:
            user = users.find_one({"f_id": str(f_id)})
            if not user:
                users.insert({"f_id": str(f_id), "name": name, "date": datetime.datetime.utcnow()})
            likes.insert({"pug_id": str(pug_id), "f_id": str(f_id), "date": datetime.datetime.utcnow()})
            if is_number(pug_id):
                pugs.update({'id': int(pug_id)}, {'$inc': {'likes': 1}})
            else:
                pugs.update({'id': pug_id}, {'$inc': {'likes': 1}})
            return jsonify({'msg':'success'})
    else:
        return jsonify({'msg':'error', 'error':'you should login first'})
# PUG GENERATORS

@app.route("/pugs")
def random_pugs():
    rand = int(random.random()*pugs.find({"animated": 1}).count())
    pug = pugs.find({"animated": 1}).limit(-1).skip(rand).next()
    return jsonify({'pug_id': str(pug['id']), 'likes': pug['likes'], 'url': pug['url']})

@app.route("/pugs_static")
def random_static_pugs():
    rand = int(random.random()*pugs.find({"animated": 0}).count())
    pug = pugs.find({"animated": 0}).limit(-1).skip(rand).next()
    return jsonify({'pug_id': str(pug['id']), 'likes': pug['likes'], 'url': pug['url']})

@app.route("/pugs_mixed")
def random_mixed_pugs():
    rand = int(random.random()*pugs.find().count())
    pug = pugs.find().limit(-1).skip(rand).next()
    return jsonify({'pug_id': str(pug['id']), 'likes': pug['likes'], 'url': pug['url']})

if __name__ == "__main__":
    app.run()
