# Cameron Lohman
# CMSC426 - Assignment2 - Product_Service

import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'products.sqlite')
db = SQLAlchemy(app)

# Product model
class Product(db.Model):
    product_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

# Endpoint to get all products
@app.route('/products', methods=['GET'])
def get_grocery_products():
    products = Product.query.all()
    product_list = [{"product_id": product.product_id, "name": product.name, "price": product.price, "quantity": product.quantity} for product in products]
    return jsonify({"products": product_list})


# Endpoint to get a product by ID
@app.route('/products/<int:product_id>', methods=['GET'])
def get_product_id(product_id):
    product = Product.query.get(product_id)
    if product:
        return jsonify({"product": {"product_id": product.product_id, "name": product.name, "price": product.price, "quantity": product.quantity}})
    else:
        return jsonify({"error": "Product not found"}), 404


# Endpoint to add a new product
@app.route('/products', methods=['POST'])
def add_product():
    data = request.json
    new_product = Product(
        name=data["name"],
        price=data["price"],
        quantity=data["quantity"]
    )
    db.session.add(new_product) 
    db.session.commit()

    return jsonify({"message": "Product added", "product": {"name": new_product.name, "price": new_product.price, "quantity": new_product.quantity}}), 201


if __name__ == '__main__':
    # with app.app_context():
    #     db.create_all()
    app.run(debug=True, port=5000)

