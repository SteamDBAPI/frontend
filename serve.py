#!/usr/bin/python3

from flask import Flask, jsonify, abort, make_response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

#Globals
engine = create_engine('sqlite:///games.db')
app = Flask(__name__, static_url_path="")
game_list = []

def build_list(session):
    global game_list
    result = session.execute('SELECT * FROM games')
    for game in result:
        game_list.append(game.id)

@app.route('/api/v1/list', methods=['GET'])
def list():
    global game_list
    return jsonify({'games': game_list})

if __name__ == '__main__':
    Session = sessionmaker(bind=engine)
    session = Session()
    build_list(session)
    app.run(host="0.0.0.0", port=8080, debug=True)
