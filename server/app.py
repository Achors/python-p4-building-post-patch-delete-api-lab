#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate

from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return '<h1>Bakery GET-POST-PATCH-DELETE API</h1>'

@app.route('/bakeries')
def bakeries():
    bakeries = [bakery.to_dict() for bakery in Bakery.query.all()]
    return make_response(  bakeries,   200  )

@app.route('/bakeries/<int:id>')
def bakery_by_id(id):

    bakery = Bakery.query.filter_by(id=id).first()
    bakery_serialized = bakery.to_dict()
    return make_response ( bakery_serialized, 200  )

@app.route('/baked_goods/by_price')
def baked_goods_by_price():
    baked_goods_by_price = BakedGood.query.order_by(BakedGood.price.desc()).all()
    baked_goods_by_price_serialized = [
        bg.to_dict() for bg in baked_goods_by_price
    ]
    return make_response( baked_goods_by_price_serialized, 200  )
   

@app.route('/baked_goods/most_expensive')
def most_expensive_baked_good():
    most_expensive = BakedGood.query.order_by(BakedGood.price.desc()).limit(1).first()
    most_expensive_serialized = most_expensive.to_dict()
    return make_response( most_expensive_serialized,   200  )


@app.route('/baked_goods', methods=['POST'])
def create_baked_good():
    data = request.get_json()
    if 'name' not in data or 'price' not in data:
        return jsonify({"error": "Name and price are required"}), 400


    if not isinstance(data['name'], str) or not isinstance(data['price'], (int, float)):
        return jsonify({"error": "Invalid data format"}), 400

    new_baked_good = BakedGood(name=data['name'], price=data['price'])

    try:
        db.session.add(new_baked_good)
        db.session.commit()
        return jsonify(new_baked_good.to_dict()), 201
    except Exception as e:
        return jsonify({"error": "Failed to create baked good"}), 500

@app.route('/bakeries/<int:id>', methods=['PATCH'])
def update_bakery(id):
    data = request.get_json()
    bakery = Bakery.query.get(id)

    if bakery:
        bakery.name = data.get('name', bakery.name)

        try:
            db.session.commit()
            return jsonify(bakery.to_dict())
        except Exception as e:
            return jsonify({"error": "Failed to update bakery"}), 500
    else:
        return jsonify({"error": "Bakery not found"}), 404

@app.route('/baked_goods/<int:id>', methods=['DELETE'])
def delete_baked_good(id):
    baked_good = BakedGood.query.get(id)

    if baked_good:
        try:
            db.session.delete(baked_good)
            db.session.commit()
            return jsonify({"message": "Baked good deleted successfully"})
        except Exception as e:
            return jsonify({"error": "Failed to delete baked good"}), 500
    else:
        return jsonify({"error": "Baked good not found"}), 404

if __name__ == '__main__':
    app.run(port=5555, debug=True)