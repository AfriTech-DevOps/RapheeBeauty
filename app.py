from flask import Flask, render_template, request, redirect, url_for, flash, make_response, blueprints, jsonify, Response, send_file, g
from flask_sqlalchemy import SQLAlchemy
# from werkzeug.security import generate_password_hash, check_password_hash
from passlib.hash import sha256_crypt
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from wtforms import SelectField
from flask_cors import CORS
from flask_migrate import Migrate
# from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from functools import wraps
import mysql.connector as mysql
from mysql.connector import Error
import sqlite3 as sql
import database
import os
import random
from dotenv import load_dotenv
from models import User

load_dotenv()

app = Flask(__name__)
CORS(app, origins=['http://localhost:5000', 'https://rapheebeauty.com', 'https://www.rapheebeauty.com', 
                   'https://rapheebeauty.herokuapp.com', 'https://www.rapheebeauty.herokuapp.com',
                   'https://rapheebeauty.netlify.app', 'https://www.rapheebeauty.netlify.app'], supports_credentials=True)
token = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz1234567890', 32))
app.secret_key = token
# app.config['SECRET_KEY'] = token
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
# app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}:3306/{os.getenv('MYSQL_DATABASE')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
session = {}

config = {
    'host': os.getenv('MYSQL_HOST'),
    'port': 3306,
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DATABASE')
}


def get_db_connection():
    conn = sql.connect('rapheeBeauty-database.db', check_same_thread=False)
    return conn
    # with app.app_context():
    #     if 'db_connection' not in g:
    #         g.db_connection = mysql.connect(**config)
    #     return g.db_connection



database.create_user_table(get_db_connection())
# try:
#     with mysql.connect(**config) as conn:
#         cursor = conn.cursor()
#         if conn.is_connected():
#             print("Connected to MySQL database")
#             database.create_user_table(conn)
# except Error as e:
#     print(e)

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

class ProductCat(FlaskForm):
    product_cats = SelectField('Gender', choices=['Select Category', 'Fragrances', 'Skincare', 'Makeup', 'Haircare', 'Bodycare', 'Accessories', 'Gifts', 'Brands'])


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session and session['logged_in']:
            print("User is logged in")
            return f(*args, **kwargs)
        else:
            flash("You need to login for access")
            return redirect(url_for('login'))
    return wrap

# @app.errorhandler(404)
# @app.route('/error')
# def error_page():
#     return make_response(render_template('404.html'), headers)

@app.route('/login', methods=['GET', 'POST'])
def login():
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        email = request.form.get('email').lower()
        password = request.form.get('tp_password')
        with app.app_context():
            cursor.execute(f"SELECT * FROM customer WHERE email = '{email}'")
            customer = cursor.fetchone()
            print(customer)
            if customer and sha256_crypt.verify(password, customer[3]):
                flash('Logged in successfully.', 'success')
                session['logged_in'] = True
                session['email'] = email
                session['id'] = customer[0]
                session['current_user'] = customer[1]
                session['is_superuser'] = customer[4]
                session['cookie'] = token
                return redirect(url_for('profile'))
            else:
                flash('Invalid Credentials.', 'danger')
                return redirect(url_for('login'))
    return make_response(render_template('login.html'), headers)

@app.route('/register', methods=['GET', 'POST'])
def register():
    conn = get_db_connection()
    if request.method == 'POST':
        full_name = request.form.get('name')
        email = request.form.get('email').lower()
        password = request.form.get('tp_password')

        print(f"full_name: {full_name}, email: {email}, password: {password}")
        with app.app_context():
            database.insert_customer_data(conn, full_name, email, sha256_crypt.encrypt(password), False)
            return redirect(url_for('login'))
    
    else:
        return make_response(render_template('register.html'), headers)


@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route('/' , methods=['GET', 'POST'])
def index():
    product_cats = ['Select Category', 'Fragrances', 'Skincare', 'Makeup', 'Haircare', 'Bodycare', 'Accessories', 'Gifts', 'Brands']
    product_cats_form = ProductCat()
    selected_cat = ''
    if selected_cat == 'Select Category' or selected_cat == 'Fragrances' or selected_cat == 'Skincare' or selected_cat == 'Makeup' or selected_cat == 'Haircare' or selected_cat == 'Bodycare' or selected_cat == 'Accessories' or selected_cat == 'Gifts' or selected_cat == 'Brands':
        return make_response(render_template('index.html', product_cats_form=product_cats_form, product_cats=product_cats, selected_cat=selected_cat), headers)
    return make_response(render_template('index.html', product_cats_form=product_cats_form, product_cats=product_cats), headers)

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

@login_required
@app.route('/wishlist')
def wishlist():
    return make_response(render_template('wishlist.html'), headers)

# @login_required
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = session['current_user']
    with app.app_context():
        return make_response(render_template('profile.html', user=user), headers)

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