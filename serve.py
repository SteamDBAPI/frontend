#!/usr/bin/env python

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

class Games(object):
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
    engine = create_engine('sqlite:///games.db')
    metadata = MetaData(engine)
    games_db = Table('games', metadata, autoload=True)
    mapper(Games, games_db)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

def build_list(session):
    global game_list
    result = session.query(Games).all()
    for game in result:
        game_list.append(str(game.id) + ":" + game.name)
    session.close()

@app.route('/')
def index():
    return "Welcome! Please use the /api/v1 address for access<br>Ex. /api/v1/list"

@app.route('/api/v1/list', methods=['GET'])
@login_required
def list():
    #GET: http://localhost:8000/protected/?token=admin1:password1
    return jsonify({'games': game_list})

@app.route('/api/v1/dollar', methods=['GET'])
def dollar_games():
    dollars = {}
    try:
        results = session.query(Games).filter(and_(Games.final_price <= 100, Games.init_price >= 499)).all()
    except NoResultFound:
        print("No games found :-(")
    session.close()
    for game in results:
        dollars[game.name] = game.final_price
    return Response(json.dumps(dollars))

@app.route('/api/v1/<gameid>', methods=['GET'])
def game_dump(gameid):
    try:
        result = session.query(Games).filter_by(id=gameid).one()
    except NoResultFound:
        return "No results found for that ID"
    session.close()
    return jsonify({'name': result.name, 'init_price': result.init_price, 'lowest_price': result.lowest_price, 'highest_price': result.highest_price, 'final_price': result.final_price, 'last_update': result.last_update})

if __name__ == '__main__':
    session = loadSession()
    build_list(session)
    app.run(port=8000, debug=True, use_reloader=True, extra_files=['games.db'])
