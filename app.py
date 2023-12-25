from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response, blueprints, jsonify, Response, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
import random

app = Flask(__name__)
CORS(app)
token = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz1234567890', 32))
app.secret_key = token
app.config['SECRET_KEY'] = token
app.config['SESSION_COOKIE_NAME'] = 'session'
app.config['SESSION_COOKIE_HTTPONLY'] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_DOMAIN'] = '.rapheebeauty.com'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600
app.config['SESSION_REFRESH_EACH_REQUEST'] = True
app.config['SESSION_COOKIE_PATH'] = '/'
app.config['FLASK_ENV'] = 'development'
app.config['DEBUG'] = True
app.config['TESTING'] = True
app.config['FLASK_APP'] = 'app.py'


headers = {
    'Content-Type': 'text/html',
    'charset': 'utf-8',
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With",
    "Authorization": "Bearer " + token,
    "Session-Cookie-Domain": app.config['SESSION_COOKIE_DOMAIN'],
    "Session-Cookie-Path": app.config['SESSION_COOKIE_PATH'],
    "Session-Cookie-Secure": app.config['SESSION_COOKIE_SECURE'],
    "Session-Cookie-HttpOnly": app.config['SESSION_COOKIE_HTTPONLY'],
    "Session-Cookie-SameSite": app.config['SESSION_COOKIE_SAMESITE'],
    "Session-Cookie-Name": app.config['SESSION_COOKIE_NAME']
}



login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost:3306/rapheebeauty'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(100))
    lname = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email').lower()
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                flash('Logged in successfully.', 'success')
                return redirect(url_for('home'))
            else:
                flash('Incorrect password.', 'danger')
                return redirect(url_for('login'))
        else:
            flash('Email does not exist.', 'danger')
            return redirect(url_for('login'))
    return make_response(render_template('login.html'), headers)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        email = request.form.get('email').lower()
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', 'danger')
            return redirect(url_for('register'))
        else:
            new_user = User(fname=fname, lname=lname, email=email, password=generate_password_hash(password, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully.', 'success')
            return redirect(url_for('login'))
    return make_response(render_template('register.html'), headers)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route('/')
def index():
    return make_response(render_template('index.html'), headers)

@app.route('/contact')
def contact():
    return make_response(render_template('contact.html'), headers)

@app.route('/shop')
def shop():
    return make_response(render_template('shop.html'), headers)

@app.route('/shop_list')
def shop_list():
    return make_response(render_template('shop-list.html'), headers)

@app.route('/about')
def about():
    return make_response(render_template('about.html'), headers)

@app.route('/wishlist')
def wishlist():
    return make_response(render_template('wishlist.html'), headers)

@app.route('/profile')
def profile():
    return make_response(render_template('profile.html'), headers)

@app.route('/cart')
def cart():
    return make_response(render_template('cart.html'), headers)

@app.route('/coupon')
def coupon():
    return make_response(render_template('coupon.html'), headers)

@app.route('/checkout')
def checkout():
    return make_response(render_template('checkout.html'), headers)

@app.route('/product_details')
def product_details():
    return make_response(render_template('product_details.html'), headers)

@app.route('/product_details_countdown')
def product_details_countdown():
    return make_response(render_template('product-details-countdown.html'), headers)

@app.route('/product_details_gallery')
def product_details_gallery():
    return make_response(render_template('product-details-gallery.html'), headers)

@app.route('/product_details_progress')
def product_details_progress():
    return make_response(render_template('product-details-progress.html'), headers)

@app.route('/product_details_swatches')
def product_details_swatches():
    return make_response(render_template('product-details-swatches.html'), headers)

@app.route('/product_details_list')
def product_details_list():
    return make_response(render_template('product-details-list.html'), headers)

@app.route('/compare')
def compare():
    return make_response(render_template('compare.html'), headers)

@app.route('/404')
def error():
    return make_response(render_template('404.html'), headers)

@app.route('/forgot_password')
def forgot():
    return make_response(render_template('forgot.html'), headers)

@app.route('/orders')
def order():
    return make_response(render_template('order.html'), headers)

@app.route('/shop_category')
def shop_category():
    return make_response(render_template('shop-category.html'), headers)

@app.route('/shop_1600')
def shop_1600():
    return make_response(render_template('shop-1600.html'), headers)

@app.route('/shop_filter_dropdown')
def shop_filter_dropdown():
    return make_response(render_template('shop-filter-dropdown.html'), headers)

@app.route('/shop_filter_offcanvas')
def shop_filter_offcanvas():
    return make_response(render_template('shop-filter-offcanvas.html'), headers)

@app.route('/shop_full_width')
def shop_full_width():
    return make_response(render_template('shop-full-width.html'), headers)

@app.route('/shop_infinite_scroll')
def shop_infinite_scroll():
    return make_response(render_template('shop-infinite-scroll.html'), headers)

@app.route('/shop_no_sidebar')
def shop_no_sidebar():
    return make_response(render_template('shop-no-sidebar.html'), headers)

@app.route('/shop_right_sidebar')
def shop_right_sidebar():
    return make_response(render_template('shop-right-sidebar.html'), headers)

@app.route('/shop_masonary')
def shop_masonary():
    return make_response(render_template('shop-masonary.html'), headers)

@app.route('/404')
def error_page():
    return make_response(render_template('404.html'), headers)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)