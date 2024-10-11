#!/usr/bin/env python3

from flask import Flask, jsonify, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource, reqparse

from models import db, Plant

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)


class Plants(Resource):

    def get(self):
        plants = [plant.to_dict() for plant in Plant.query.all()]
        return make_response(jsonify(plants), 200)

    def post(self):
        data = request.get_json()

        new_plant = Plant(
            name=data['name'],
            image=data['image'],
            price=data['price'],
        )

        db.session.add(new_plant)
        db.session.commit()

        return make_response(new_plant.to_dict(), 201)


api.add_resource(Plants, '/plants')


class PlantByID(Resource):

    def get(self, id):
        plant = Plant.query.filter_by(id=id).first().to_dict()
        return make_response(jsonify(plant), 200)


api.add_resource(PlantByID, '/plants/<int:id>')


class UpdatePlant(Resource):
    
    def patch(self, id):
        # Use reqparse to handle request arguments
        parser = reqparse.RequestParser()
        parser.add_argument('is_in_stock', type=bool, required=True)
        args = parser.parse_args()

        # Fetch the plant by ID
        plant = Plant.query.filter(Plant.id == id).first()
        if not plant:
            return {'message': 'Plant not found'}, 404

        # Update the is_in_stock field if it's present in the request
        if 'is_in_stock' in args:
            plant.is_in_stock = args['is_in_stock']

        # Commit the changes
        db.session.commit()

        # Return the updated plant as a JSON response
        return make_response(jsonify(plant.to_dict()), 200)
    
api.add_resource(UpdatePlant, '/plants/<int:id>')


class DeletePlant(Resource):

    def delete(self, id):
        plant = Plant.query.filter(Plant.id == id).first()
        if not plant:
            return {'message': 'Plant not found'}, 404

        db.session.delete(plant)
        db.session.commit()

        return '', 204
            
api.add_resource(DeletePlant, '/plants/<int:id>')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
