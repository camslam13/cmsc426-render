# Cameron Lohman
# CMSC426 - Assignment2 - Cart_Service

import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import requests
basedir = os.path.abspath(os.path.dirname(__file__))

# URL of the Product Service on render
PRODUCT_SERVICE_URL = "https://productservice-aiqd.onrender.com/products"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'cart.sqlite')
db = SQLAlchemy(app)

# Define the Cart model
class CartItem(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)

# Endpoint to get the current cart for a user
@app.route('/cart/<int:user_id>', methods=['GET'])
def get_current_cart(user_id):
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    user_cart = [{"product_name": item.product_name, "quantity": item.quantity, "total_price": item.total_price} for item in cart_items]
    return jsonify({"cart": user_cart})

# Endpoint to add a product to the user's cart
@app.route('/cart/<int:user_id>/add/<int:product_id>', methods=['POST'])
def add_to_cart(user_id, product_id):
    # Get product details from the Product Service
    response = requests.get(f"{PRODUCT_SERVICE_URL}/{product_id}")
    if response.status_code == 200:
        product = response.json()["product"]
        quantity = request.json["quantity"]

        # Check if product already in the cart
        existing_item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
        if existing_item:
            existing_item.quantity += quantity
            existing_item.total_price = existing_item.quantity * product["price"]
        else:
            new_item = CartItem(
                user_id=user_id,
                product_id=product_id,
                product_name=product["name"],
                quantity=quantity,
                total_price=product["price"] * quantity
            )
            db.session.add(new_item)

        db.session.commit()
        return jsonify({"message": "Product added to cart"}), 201
    else:
        return jsonify({"error": "Product not found"}), 404

# Endpoint to remove a product from the user's cart
@app.route('/cart/<int:user_id>/remove/<int:product_id>', methods=['POST'])
def remove_from_cart(user_id, product_id):
    cart_item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify({"message": "Product removed from cart"}), 200
    else:
        return jsonify({"Error": "Product not found in cart"}), 404

if __name__ == '__main__':
    # db.create_all()
    app.run(debug=True, port=5001)
