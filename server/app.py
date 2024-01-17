#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return ''

@app.route('/scientists', methods = ['GET', 'POST'])
def scientists():
    if request.method == 'GET':
        scientists = Scientist.query.all()

        scientists_dict = [scientist.to_dict(rules = ('-missions', )) for scientist in scientists]

        response = make_response(
            scientists_dict,
            200
        )
    elif request.method == 'POST':
        try:
            form_data = request.get_json()

            new_scientist = Scientist(
                name = form_data['name'],
                field_of_study = form_data['field_of_study']
            )

            db.session.add(new_scientist)
            db.session.commit()

            response = make_response(
                new_scientist.to_dict(),
                201
            )
        except ValueError:
            response = make_response(
                { "errors": ["validation errors"] },
                400
            )

    return response

@app.route('/scientists/<int:id>', methods = ['GET', 'PATCH', 'DELETE'])
def scientist_by_id(id):
    scientist = Scientist.query.filter(Scientist.id == id).first()

    if scientist:
        if request.method == 'GET':
            response = make_response(
                scientist.to_dict(),
                200
            )
        elif request.method == 'PATCH':
            try:
                form_data = request.get_json()
                
                for attr in form_data:
                    setattr(scientist, attr, form_data[attr])

                db.session.commit()

                response = make_response(
                    scientist.to_dict(),
                    202
                )
            except ValueError:
                response = make_response(
                    { "errors": ["validation errors"] },
                    400
                )
        elif request.method == 'DELETE':
            try:
                assoc_missions = Mission.query.filter(Mission.scientist_id == id).all()

                for assoc_mission in assoc_missions:
                    db.session.delete(assoc_mission)
            
                db.session.delete(scientist)
                db.session.commit()
            
                response = make_response(
                    {},
                    204
                )
            except ValueError:
                response = make_response(
                    { "error": "Scientist not found" },
                    404
                )
    else:
        response = make_response(
            { "error": "Scientist not found" },
            404
        )
    
    return response

@app.route('/planets', methods = ['GET'])
def planets():
    planets = Planet.query.all()

    planets_dict = [planet.to_dict(rules = ('-missions', )) for planet in planets]

    response = make_response(
        planets_dict,
        200
    )

    return response

@app.route('/missions', methods = ['POST'])
def missions():
    try:
        form_data = request.get_json()

        new_mission = Mission(
            name = form_data['name'],
            planet_id = form_data['planet_id'],
            scientist_id = form_data['scientist_id']
        )

        db.session.add(new_mission)
        db.session.commit()

        response = make_response(
            new_mission.to_dict(),
            201
        )
    except ValueError:
        response = make_response(
            { "errors": ["validation errors"] },
            400
        )
    
    return response


if __name__ == '__main__':
    app.run(port=5555, debug=True)
