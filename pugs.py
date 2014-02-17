from pymongo import MongoClient
import random
from flask import Flask, render_template, url_for, session, request, redirect
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
    return redirect(url_for('check', _external=True))

@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')

@app.route('/check')
def check():
    me = facebook.get('/me')
    return 'Logged in as id=%s name=%s redirect=%s' % \
        (me.data['id'], me.data['name'], request.args.get('next'))

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
