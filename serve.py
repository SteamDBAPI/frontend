#!/usr/bin/python3

from flask import Flask, jsonify, abort, make_response
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker, mapper
from sqlalchemy.orm.exc import NoResultFound

#Globals
app = Flask(__name__, static_url_path="")
game_list = []

class Games(object):
    pass

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
def list():
    return jsonify({'games': game_list})

@app.route('/api/v1/<gameid>', methods=['GET'])
def game_dump(gameid):
    try:
        result = session.query(Games).filter_by(id=gameid).one()
    except NoResultFound:
        return "No results found for that ID"
    session.close()
    return jsonify({'name': result.name, 'lowest_price': result.lowest_price})

if __name__ == '__main__':
    session = loadSession()
    build_list(session)
    #app.run(host="0.0.0.0", port=8080, debug=True)
    app.run(port=8000, debug=True)
