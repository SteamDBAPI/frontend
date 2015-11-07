#!/usr/bin/env python3

from flask import Flask, jsonify, Response
from flask.ext.login import LoginManager, UserMixin, login_required
from sqlalchemy import create_engine, MetaData, Table, and_, or_, desc
from sqlalchemy.orm import sessionmaker, mapper
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
import json

#Globals
app = Flask(__name__, static_url_path="")
app.config["SECRET_KEY"] = "ITSASECRET"
login_manager = LoginManager()
login_manager.init_app(app)

game_list = []

class Game(object):
    pass

class Prices(object):
    pass

class User(UserMixin):

    def __init__(self, api_key):
        self.api_key = api_key

@login_manager.request_loader
def load_user(request):
    api_key = request.args.get('api_key')
    if api_key:
        #For testing... echo -n user | md5sum
        user = User("ee11cbb19052e40b07aac0ca060c23ee")
        if api_key == user.api_key:
            return user
    return None

def load_user_old(request):
    #Defunct code for now, do not use!
    #Code borrowed from: http://thecircuitnerd.com/flask-login-tokens
    token = request.headers.get('Authorization')
    if token is None:
        token = request.args.get('token')

    if token is not None:
        username,password = token.split(":")
        check_pass = User.get(username)
        if (check_pass is not None):
            user = User(username,password)
            if check_pass == password:
                return user
    return None

def loadSession():
    engine = create_engine('sqlite:///games.db', echo=False)
    metadata = MetaData(engine)
    games_db = Table('games', metadata, autoload=True)
    prices_db = Table('prices', metadata, autoload=True)
    mapper(Game, games_db)
    mapper(Prices, prices_db)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

def build_list(session):
    global game_list
    result = session.query(Game).all()
    for game in result:
        game_list.append(str(game.id) + ":" + game.name)
    session.close()

@app.route('/')
def index():
    return "Welcome! Please use the /api/v1 address for access<br>Ex. /api/v1/games/list<br/>"

@app.route('/robots.txt')
def robots_txt():
    return "User-agent: *<br/>Disallow: /<br/>"

@app.route('/api/v1/games/list', methods=['GET'])
@login_required
def list():
    return jsonify({'games': game_list})

@app.route('/api/v1/games/dollar', methods=['GET'])
@login_required
def dollar_games():
    dollars = {}
    try:
        results = session.query(Game, Prices).filter(Prices.final_price <= 100, Prices.initial_price >= 499, Game.id==Prices.id).all()
    except NoResultFound:
       return "No games matching criteria found"
    session.close()
    for game in results:
        dollars.update({game[0].name: {'initial_price': game[1].initial_price, 'final_price': game[1].final_price}})
    return jsonify({'dollar_games': dollars})

@app.route('/api/v1/games/discount<int:pcent>', methods=['GET'])
@login_required
def discount(pcent):
    discount = {}
    base_url = "http://store.steampowered.com/app/{}"
    try:
        results = session.query(Game, Prices).filter(Prices.discount_percent >= pcent, Game.id==Prices.id).order_by(Prices.timestamp.desc()).all()
    except NoResultFound:
        return "No current discounts found. Odd"
    session.close()
    for game in results:
        discount.update({ game[0].name : {'initial_price': game[1].initial_price, 'final_price': game[1].final_price, 'discount_percent': game[1].discount_percent, 'url': base_url.format(game[0].id)}})
    return jsonify({'discount': discount})

@app.route('/api/v1/games/<int:gameid>', methods=['GET'])
@login_required
def game_dump(gameid):
    try:
        result = session.query(Game, Prices).filter(Game.id==gameid).filter(Prices.id==gameid).order_by(Prices.timestamp.desc()).limit(1).one()
    except NoResultFound:
        return "No results found for that ID"
    except MultipleResultsFound:
        return "Multiple results found. This is a bug!"
    session.close()
    return jsonify({'name': result[0].name, 'initial_price': result[1].initial_price, 'final_price': result[1].final_price, 'discount_percent': result[1].discount_percent, 'timestamp': result[1].timestamp})

if __name__ == '__main__':
    session = loadSession()
    build_list(session)
    app.run(port=8000, debug=False, use_reloader=True, extra_files=['games.db'])
