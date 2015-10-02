#!/usr/bin/env python3

from flask import Flask, jsonify, Response
from flask.ext.login import LoginManager, UserMixin, login_required
from sqlalchemy import create_engine, MetaData, Table, and_, or_
from sqlalchemy.orm import sessionmaker, mapper
from sqlalchemy.orm.exc import NoResultFound
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
    user_database = {"admin1": "password1",
                     "admin2": "password2"}

    def __init__(self, username, password):
        self.id = username
        self.password = password

    @classmethod
    def get(cls,id):
        return cls.user_database.get(id)

@login_manager.request_loader
def load_user(request):
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
    return "Welcome! Please use the /api/v1 address for access<br>Ex. /api/v1/games/list"

@app.route('/api/v1/games/list', methods=['GET'])
@login_required
def list():
    #GET: http://localhost:8000/protected/?token=admin1:password1
    return jsonify({'games': game_list})

@app.route('/api/v1/games/dollar', methods=['GET'])
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
def discount(pcent):
    discount = {}
    try:
        results = session.query(Game, Prices).filter(Prices.discount_percent >= pcent, Game.id==Prices.id).all()
    except NoResultFound:
        return "No current discounts found. Odd"
    session.close()
    for game in results:
        discount.update({ game[0].name : {'initial_price': game[1].initial_price, 'final_price': game[1].final_price}})
    return jsonify({'discount': discount})

@app.route('/api/v1/games/<int:gameid>', methods=['GET'])
def game_dump(gameid):
    try:
        result = session.query(Game, Prices).filter(Game.id==gameid).filter(Prices.id==gameid).one()
    except NoResultFound:
        return "No results found for that ID"
    session.close()
    return jsonify({'name': result[0].name, 'initial_price': result[1].initial_price, 'final_price': result[1].final_price, 'discount_percent': result[1].discount_percent, 'timestamp': result[1].timestamp})

if __name__ == '__main__':
    session = loadSession()
    build_list(session)
    app.run(port=8000, debug=False, use_reloader=True, extra_files=['games.db'])
