from flask import Flask, render_template, redirect, url_for, session, flash, request
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from werkzeug.security import generate_password_hash, check_password_hash
import stripe
import requests

load_dotenv()
stripe.api_key = os.getenv("STRIPE_API_KEY")
DOMAIN = "http://localhost:5000"


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cart.db'
db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(1000), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    products = db.relationship('Product', backref='category', lazy=True)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    cart_items = db.relationship('Cart', backref='user', lazy=True)

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quantity = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product = db.relationship('Product', backref='cart_items')

@app.route('/')
def home():
    products = Product.query.all()
    return render_template('home.html', products=products)

@app.route('/category/<int:category_id>')
def category_products(category_id):
    products = Product.query.filter_by(category_id=category_id).all()
    return render_template('home.html', products=products)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            flash('Please enter your username and password.', 'warning')
            return redirect(url_for('login'))
        user = User.query.filter_by(name=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['password'] = user.password
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            flash('Passwords do not match', 'warning')
            return redirect(url_for('register'))
        existing_user = User.query.filter_by(name=username).first()
        if existing_user:
            flash('Username already taken', 'danger')
            return redirect(url_for('register'))
        hashed_password = generate_password_hash(password)
        new_user = User(name=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('password', None)
    return redirect(url_for('home'))

@app.route('/add/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'user_id' not in session:
        flash('You must be logged in to add a product', 'warning')
        return redirect(url_for('login'))
    user_id = session['user_id']
    existing_item = Cart.query.filter_by(user_id = user_id, product_id = product_id).first()
    if existing_item:
        existing_item.quantity += 1
    else:
        new_item = Cart(user_id = user_id, product_id = product_id, quantity=1)
        db.session.add(new_item)
    db.session.commit()
    flash("item added to cart successfully", 'success')
    return redirect(url_for('show_cart'))

@app.route('/cart')
def show_cart():
    if 'user_id' not in session:
        flash('You must be logged in to view a cart', 'warning')
        return redirect(url_for('login'))
    cart_items = Cart.query.filter_by(user_id = session['user_id']).all()
    total_price = sum(item.quantity * item.product.price for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    if 'user_id' not in session:
        flash('You must be logged in to checkout', 'warning')
        return redirect(url_for('login'))

    cart_items = Cart.query.filter_by(user_id=session['user_id']).all()
    if not cart_items:
        flash("Your cart is empty.", "warning")
        return redirect(url_for('show_cart'))

    line_items = []
    total_inr = 0

    for item in cart_items:
        product = item.product
        amount_paise = int(round(product.price * 100))
        total_inr += product.price * item.quantity
        line_items.append({
            'price_data': {
                'currency': 'inr',
                'product_data': {'name': product.name},
                'unit_amount': amount_paise,
            },
            'quantity': item.quantity,
        })

    print("LINE ITEMS DEBUG:", line_items)
    print("TOTAL:", total_inr)

    MIN_ORDER_AMOUNT_INR = 50
    if total_inr < MIN_ORDER_AMOUNT_INR:
        flash(f"Minimum order amount is ₹{MIN_ORDER_AMOUNT_INR}. Please add more items.", "warning")
        return redirect(url_for('show_cart'))

    session_checkout = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url="http://localhost:5000/payment-success",
        cancel_url="http://localhost:5000/cart",
    )

    return redirect(session_checkout.url, code=303)


@app.route('/payment-success')
def payment_success():
    flash("Payment successful! 🎉 Thank you for shopping with ShopEase.", "success")
    # optional: clear user’s cart after payment
    Cart.query.filter_by(user_id=session['user_id']).delete()
    db.session.commit()
    return render_template('payment_success.html')


@app.route('/remove/<int:product_id>')
def remove_from_cart(product_id):
    item = Cart.query.filter_by(user_id = session['user_id'], product_id = product_id).first()
    db.session.delete(item)
    db.session.commit()
    flash("item removed from cart successfully", 'success')
    return redirect(url_for('show_cart'))

@app.route('/increase_quantity/<int:product_id>', methods=['POST'])
def increase_quantity(product_id):
    item = Cart.query.filter_by(user_id = session['user_id'], product_id = product_id).first()
    item.quantity += 1
    db.session.commit()
    return redirect(url_for('show_cart'))

@app.route('/decrease_quantity/<int:product_id>', methods=['POST'])
def decrease_quantity(product_id):
    item = Cart.query.filter_by(user_id = session['user_id'], product_id = product_id).first()
    item.quantity -= 1
    db.session.commit()
    return redirect(url_for('show_cart'))

@app.route('/search')
def search():
    query = request.args.get('query', '').strip()

    if not query:
        # If search box empty, show all products
        products = Product.query.all()
    else:
        # Search by product name or description (case-insensitive)
        products = Product.query.filter(
            (Product.name.ilike(f"%{query}%")) |
            (Product.description.ilike(f"%{query}%"))
        ).all()

    return render_template('search.html', products=products, query=query)


@app.route('/import-products')
def import_products():
    """Imports products from FakeStore API once."""
    if Product.query.count() > 0:
        return "Products already exist. Skipping import.", 200

    for i in range(1, 21):
        if i < 5:
            category_id = 1
        elif i >= 15:
            category_id = 2
        elif 8 < i < 15:
            category_id = 3
        else:
            category_id = 4
        response = requests.get(f'https://fakestoreapi.com/products/{i}')
        if response.status_code != 200:
            continue
        data = response.json()

        new_product = Product(
            id=data['id'],
            name=data['title'],
            description=data['description'],
            price=data['price'],
            image=data['image'],
            category_id= category_id
        )
        db.session.add(new_product)

    db.session.commit()
    return "Products imported successfully!"




with app.app_context():
    db.create_all()




if __name__ == '__main__':
    app.run(debug=True)