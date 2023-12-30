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
database.create_cart_table(get_db_connection())
database.create_wishlist_table(get_db_connection())
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
    product_cats = SelectField('Gender', choices=['Select Category', 'Fragrance', 'Skincare', 'Makeup', 'Hair', 'Bodycare'])


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
                headers['SESSIONID'] = f"{session['cookie']}-{session['id']}-{session['email']}"
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


@app.route('/home')
@app.route('/' , methods=['GET', 'POST'])
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    random_products_query = """SELECT * FROM products ORDER BY RANDOM() LIMIT 8"""
    cursor.execute(random_products_query)
    random_products = cursor.fetchall()


    product_cats = ['Select Category', 'Fragrance', 'Skincare', 'Makeup', 'Haircare', 'Bodycare']
    product_cats_form = ProductCat()
    selected_cat = ''


    fragrance_count_query = """SELECT COUNT(*) FROM products WHERE category='fragrance'"""
    skincare_count_query = """SELECT COUNT(*) FROM products WHERE category='skincare'"""
    makeup_count_query = """SELECT COUNT(*) FROM products WHERE category='makeup'"""
    haircare_count_query = """SELECT COUNT(*) FROM products WHERE category='hair'"""
    bodycare_count_query = """SELECT COUNT(*) FROM products WHERE category='bodycare'"""

    fragrance_count = cursor.execute(fragrance_count_query).fetchone()[0]
    skincare_count = cursor.execute(skincare_count_query).fetchone()[0]
    makeup_count = cursor.execute(makeup_count_query).fetchone()[0]
    haircare_count = cursor.execute(haircare_count_query).fetchone()[0]
    bodycare_count = cursor.execute(bodycare_count_query).fetchone()[0]

    categories = []

    product_categories = ['fragrance', 'skincare', 'makeup', 'hair', 'bodycare']

    for category in product_categories:
        cursor.execute(f"SELECT COUNT(*) FROM products WHERE category='{category.lower()}'")
        count = cursor.fetchone()[0]
        cursor.execute(f"SELECT images FROM products WHERE category='{category.lower()}' AND CAST(reviews AS UNSIGNED) > 500 AND CAST(reviews AS UNSIGNED) < 3000 LIMIT 1")
        images = cursor.fetchone()[0]
        categories.append({
            'category': category.capitalize(),
            'count': count,
            'images': images
        })


    wishlist_query = """SELECT COUNT(*) FROM wishlist"""
    cursor.execute(wishlist_query)
    wishlist_count = cursor.fetchone()[0]



    if selected_cat == 'Select Category' or selected_cat == 'Fragrances' or selected_cat == 'Skincare' or selected_cat == 'Makeup' or selected_cat == 'Haircare' or selected_cat == 'Bodycare' or selected_cat == 'Accessories' or selected_cat == 'Gifts' or selected_cat == 'Brands':
        return make_response(render_template('index.html', product_cats_form=product_cats_form, product_cats=product_cats, selected_cat=selected_cat, 
                                             random_products=random_products, fragrance_count=fragrance_count, skincare_count=skincare_count, makeup_count=makeup_count,
                                             haircare_count=haircare_count, bodycare_count=bodycare_count, categories=categories, wishlist_count=wishlist_count), headers)
    return make_response(render_template('index.html', product_cats_form=product_cats_form, product_cats=product_cats, random_products=random_products, fragrance_count=fragrance_count, 
                                         skincare_count=skincare_count, makeup_count=makeup_count,
                                             haircare_count=haircare_count, bodycare_count=bodycare_count, categories=categories, wishlist_count=wishlist_count), headers)

@app.route('/contact')
def contact():
    if 'email' not in session:
        conn = get_db_connection()
        cursor = conn.cursor()
        wishlist_query = """SELECT COUNT(*) FROM wishlist"""
        cursor.execute(wishlist_query)
        wishlist_count = cursor.fetchone()[0]

    return make_response(render_template('contact.html', wishlist_count=wishlist_count), headers)

@app.route('/shop')
def shop():
    categories = ['fragrance', 'skincare', 'makeup', 'hair', 'bodycare']
    page = request.args.get('page', 1, type=int)
    per_page = 10
    conn = get_db_connection()
    cursor = conn.cursor()

    fragrance_count_query = """SELECT COUNT(*) FROM products WHERE category='fragrance'"""
    skincare_count_query = """SELECT COUNT(*) FROM products WHERE category='skincare'"""
    makeup_count_query = """SELECT COUNT(*) FROM products WHERE category='makeup'"""
    haircare_count_query = """SELECT COUNT(*) FROM products WHERE category='hair'"""
    bodycare_count_query = """SELECT COUNT(*) FROM products WHERE category='bodycare'"""

    fragrance_count = cursor.execute(fragrance_count_query).fetchone()[0]
    skincare_count = cursor.execute(skincare_count_query).fetchone()[0]
    makeup_count = cursor.execute(makeup_count_query).fetchone()[0]
    haircare_count = cursor.execute(haircare_count_query).fetchone()[0]
    bodycare_count = cursor.execute(bodycare_count_query).fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM products")
    total_count = cursor.fetchone()[0]

    num_pages = total_count // per_page + (total_count % per_page > 0)
    offset = (page - 1) * per_page

    # all_products_query = """SELECT * FROM products LIMIT ? ORDER BY RANDOM()"""
    cursor.execute("SELECT * FROM products ORDER BY RANDOM() LIMIT ? OFFSET ?", (per_page, offset))
    products = cursor.fetchall()
    # print(products)

    if 'email' not in session:
        wishlist_query = """SELECT COUNT(*) FROM wishlist"""
        cursor.execute(wishlist_query)
        wishlist_count = cursor.fetchone()[0]
    else:
        cursor.execute(f"Select id from customer where email='{session['email']}'")
        customer_id = cursor.fetchone()[0]
        cursor.execute(f"SELECT COUNT(*) FROM wishlist WHERE customer_id={customer_id}")
        wishlist_count = cursor.fetchone()[0]

    conn.close()
    return make_response(render_template('shop.html', fragrance_count=fragrance_count, skincare_count=skincare_count, makeup_count=makeup_count,
                                             haircare_count=haircare_count, bodycare_count=bodycare_count, products=products, page=page, num_pages=num_pages, 
                                             per_page=per_page, categories=categories, wishlist_count=wishlist_count), headers)


@app.route('/category/<string:category>')
def category(category):
    conn = get_db_connection()
    cursor = conn.cursor()
    

    categories = ['fragrance', 'skincare', 'makeup', 'hair', 'bodycare']
    if category not in categories:
        return redirect(url_for('error_page'))
    else:
        cursor.execute(f"SELECT COUNT(*) FROM products WHERE category='{category}'")
        total_count = cursor.fetchone()[0]
        print(total_count)
        page = request.args.get('page', 1, type=int)
        per_page = 10
        num_pages = total_count // per_page + (total_count % per_page > 0)
        offset = (page - 1) * per_page
        cursor.execute(f"SELECT * FROM products WHERE category='{category}' ORDER BY RANDOM() LIMIT ? OFFSET ?", (per_page, offset))
        products = cursor.fetchall()
        print(products)
        conn.close()
        return make_response(render_template('shop-category.html', products=products, category=category, page=page, num_pages=num_pages, per_page=per_page), headers)

@app.route('/search', methods=['GET', 'POST'])
def search():
    query = request.args.get('query', '')
    category = request.args.get('product_cats', '').lower()
    conn = get_db_connection()
    cursor = conn.cursor()
    categories = ['fragrance', 'skincare', 'makeup', 'hair', 'bodycare']
    page = request.args.get('page', 1, type=int)
    per_page = 10


    fragrance_count_query = """SELECT COUNT(*) FROM products WHERE category='fragrance'"""
    skincare_count_query = """SELECT COUNT(*) FROM products WHERE category='skincare'"""
    makeup_count_query = """SELECT COUNT(*) FROM products WHERE category='makeup'"""
    haircare_count_query = """SELECT COUNT(*) FROM products WHERE category='hair'"""
    bodycare_count_query = """SELECT COUNT(*) FROM products WHERE category='bodycare'"""

    fragrance_count = cursor.execute(fragrance_count_query).fetchone()[0]
    skincare_count = cursor.execute(skincare_count_query).fetchone()[0]
    makeup_count = cursor.execute(makeup_count_query).fetchone()[0]
    haircare_count = cursor.execute(haircare_count_query).fetchone()[0]
    bodycare_count = cursor.execute(bodycare_count_query).fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM products")
    total_count = cursor.fetchone()[0]

    num_pages = total_count // per_page + (total_count % per_page > 0)
    offset = (page - 1) * per_page

    # all_products_query = """SELECT * FROM products LIMIT ? ORDER BY RANDOM()"""
    cursor.execute("SELECT * FROM products ORDER BY RANDOM() LIMIT ? OFFSET ?", (per_page, offset))
    products = cursor.fetchall()
    # print(products)



    if query:
        if category == 'select category' or category not in categories:
            query_condition = f"product_name LIKE '%{query}%'"
        else:
            query_condition = f"product_name LIKE '%{query}%' AND category='{category}'"

        search_query = f"SELECT * FROM products WHERE {query_condition}"
        cursor.execute(search_query)
        products = cursor.fetchall()

        if not products:
            conn.close()
            return redirect(url_for('product_not_found'))
    
    wishlist_query = """SELECT COUNT(*) FROM wishlist"""
    cursor.execute(wishlist_query)
    wishlist_count = cursor.fetchone()[0]

         
    return make_response(render_template('shop-list.html', query=query, category=category, categories=categories, fragrance_count=fragrance_count, skincare_count=skincare_count, makeup_count=makeup_count,
                                             haircare_count=haircare_count, bodycare_count=bodycare_count, products=products, page=page, num_pages=num_pages, per_page=per_page, wishlist_count=wishlist_count), headers)

    
@app.route('/shop_list')
def shop_list():
    

    return make_response(render_template('shop-list.html'), headers)

@app.route('/about')
def about():
    return make_response(render_template('about.html'), headers)

@login_required
@app.route('/wishlist')
def wishlist():
    conn = get_db_connection()
    cursor = conn.cursor()
    if 'email' not in session:
        return redirect(url_for('login'))
    else:
        cursor.execute(f"Select id from customer where email='{session['email']}'")
        customer_id = cursor.fetchone()[0]
        cursor.execute(f"SELECT * FROM wishlist WHERE customer_id={customer_id}")
        wishlist = cursor.fetchall()
        print(wishlist)

        if not wishlist:
            return make_response(render_template('wishlist.html', products=[]), headers)
        
        products = []
        for item in wishlist:
            cursor.execute(f"SELECT * FROM products WHERE product_id={item[1]}")
            product = cursor.fetchone()
            if product:
                products.append(product)
            else:
                pass
        print(products)
        
        return make_response(render_template('wishlist.html', products=products, wishlist=wishlist), headers)

# @login_required
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    conn = get_db_connection()
    cursor = conn.cursor()
    user = session['current_user']
    wishlist_query = """SELECT COUNT(*) FROM wishlist"""
    cursor.execute(wishlist_query)
    wishlist_count = cursor.fetchone()[0]
    with app.app_context():
        return make_response(render_template('profile.html', user=user, wishlist_count=wishlist_count), headers)

@app.route('/cart')
def cart():
    conn = get_db_connection()
    cursor = conn.cursor()
    if 'email' not in session:
        return redirect(url_for('login'))
    else:
        cursor.execute(f"Select id from customer where email='{session['email']}'")
        customer_id = cursor.fetchone()[0]
        cursor.execute(f"SELECT * FROM cart WHERE customer_id={customer_id}")
        cart = cursor.fetchall()
        print(cart)

        if not cart:
            return make_response(render_template('cart.html', products=[], total=0, subtotal=0), headers)
        
        products = []
        subtotal = 0
        total = 0
        for item in cart:
            cursor.execute(f"SELECT * FROM products WHERE product_id={item[1]}")
            product = cursor.fetchone()

            if product:
                product_price = float(product[2].split('NGN ')[1].replace(',', ''))
                
                item_subtotal = product_price * item[3]
                products_with_subtotal = {
                    'product_id': product[0],
                    'product_name': product[1],
                    'product_price': product[2],
                    'product_discount_price': product[3],
                    'product_image': product[4],
                    'product_category': product[5],
                    'product_reviews': product[6],
                    'quantity': item[3],
                    'item_subtotal': item_subtotal
                }
                products.append(products_with_subtotal)
                total += item_subtotal
                subtotal += item_subtotal
            else:
                pass
        print(products)

        wishlist_query = """SELECT COUNT(*) FROM wishlist"""
        cursor.execute(wishlist_query)
        wishlist_count = cursor.fetchone()[0]
        
        return make_response(render_template('cart.html', products=products, total=total, subtotal=subtotal, wishlist_count=wishlist_count), headers)


@app.route('/coupon')
def coupon():
    return make_response(render_template('coupon.html'), headers)

@app.route('/checkout')
def checkout():
    return make_response(render_template('checkout.html'), headers)

@app.route('/product_details')
def product_details():
    return make_response(render_template('product-details.html'), headers)

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
@login_required
def order():
    return make_response(render_template('order.html'), headers)

@app.route('/shop_category')
def shop_category():
    conn = get_db_connection()
    cursor = conn.cursor()

    product_cat = []
    categories = ['fragrance', 'skincare', 'makeup', 'hair', 'bodycare']

    for category in categories:
       cursor.execute(f"SELECT COUNT(*) FROM products WHERE category='{category}'")
       count = cursor.fetchone()[0]
       cursor.execute(f"SELECT images FROM products WHERE category='{category}' AND CAST(reviews AS UNSIGNED) > 500 AND CAST(reviews AS UNSIGNED) < 3000 LIMIT 1")
       images = cursor.fetchone()[0]
       product_cat.append({
              'category': category,
              'count': count,
              'images': images
         })
    print(product_cat)

    wishlist_query = """SELECT COUNT(*) FROM wishlist"""
    cursor.execute(wishlist_query)
    wishlist_count = cursor.fetchone()[0]

    return make_response(render_template('shop-category.html', product_cat=product_cat, wishlist_count=wishlist_count), headers)


@app.route('/addToCart')
def add_to_cart():
    conn = get_db_connection()
    cursor = conn.cursor()
    quantity = 1
    if 'email' not in session:
        return redirect(url_for('login'))
    else:
        product_id = request.args.get('product_id')
        cursor.execute(f"Select id from customer where email='{session['email']}'")
        customer_id = cursor.fetchone()[0]
        try:
            cursor.execute(f"INSERT INTO cart (product_id, customer_id, quantity) VALUES ({product_id}, {customer_id}, {quantity})")
            conn.commit()
            msg = "Added to cart successfully"
        except Error:
            conn.rollback()
            msg = "Error occured"
        finally:
            conn.close()
    return redirect(url_for('cart'))

@app.route('/updateCart/<int:product_id>', methods=['GET', 'POST'])
def update_cart(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    qty = request.form.get('qty')

    if qty is None or not qty.isdigit():
        flash('Invalid quantity')
        return redirect(url_for('cart'))
    qty = int(qty)
    # product_id = request.args.get('product_id')
    print(qty, product_id)
    if 'email' not in session:
        return redirect(url_for('login'))
    else:
        cursor.execute(f"SELECT * FROM cart WHERE product_id={product_id} AND customer_id={session['id']}")
        cart_item = cursor.fetchone()
        if cart_item:
            new_quantity = qty
            cursor.execute(f"UPDATE cart set quantity={new_quantity} where product_id={product_id} AND customer_id={session['id']}")
            conn.commit()
            msg = "Updated cart successfully"
        else:
            msg = "Error occured"
        conn.close()
    return redirect(url_for('cart'))

@app.route('/removeFromCart/<int:product_id>')
def remove_from_cart(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    if 'email' not in session:
        return redirect(url_for('login'))
    else:
        cursor.execute(f"select * from products p join cart c on p.product_id = c.product_id where p.product_id={product_id}")
        product = cursor.fetchone()
        if product:
            if product[10] > 1:
                cursor.execute(f"UPDATE cart set quantity={product[10]-1} where product_id={product_id}")
                conn.commit()
            else:
                cursor.execute(f"DELETE from cart where product_id={product_id}")
                conn.commit()
            msg = "Removed from cart successfully"
        else:
            msg = "Error occured"
        conn.close()
    return redirect(url_for('cart'))

@app.route('/addToWishlist/<int:product_id>')
def add_to_wishlist():
    conn = get_db_connection()
    cursor = conn.cursor()
    if 'email' not in session:
        return redirect(url_for('login'))
    else:
        product_id = request.args.get('product_id')
        cursor.execute(f"Select id from customer where email='{session['email']}'")
        customer_id = cursor.fetchone()[0]
        try:
            cursor.execute(f"INSERT INTO wishlist (product_id, customer_id) VALUES ({product_id}, {customer_id})")
            conn.commit()
            msg = "Added to wishlist successfully"
        except Error:
            conn.rollback()
            msg = "Error occured"
        finally:
            conn.close()
    return redirect(url_for('wishlist'))

@app.route('/removeFromWishlist/<int:product_id>')
def remove_from_wishlist(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    qty = request.form.get('qty')


    if 'email' not in session:
        return redirect(url_for('login'))
    else:
        cursor.execute(f"select * from products p join wishlist w on p.product_id = w.product_id where p.product_id={product_id}")
        product = cursor.fetchone()
        if product:
            cursor.execute(f"DELETE from wishlist where product_id={product_id}")
            conn.commit()
            msg = "Removed from wishlist successfully"
        else:
            msg = "Error occured"
        conn.close()
    return redirect(url_for('wishlist'))

@app.route('/addWishlistToCart/<int:product_id>', methods=['GET', 'POST'])
def add_wishlist_to_cart(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    # qty = request.form.get('qty')

    if request.method == 'POST':
        qty = request.form.get('qty')
    
        if qty is None or not qty.isdigit():
            msg = 'Invalid quantity'
            return redirect(url_for('wishlist'))
        qty = int(qty)
        if 'email' not in session:
            return redirect(url_for('login'))
        else:
            cursor.execute(f"Select id from customer where email='{session['email']}'")
            customer_id = cursor.fetchone()[0]
            try:
                cursor.execute(f"INSERT INTO cart (product_id, customer_id, quantity) VALUES ({product_id}, {customer_id}, {qty})")
                conn.commit()
                msg = "Added to cart successfully"
            except Error:
                conn.rollback()
                msg = "Error occured"
            finally:
                conn.close()
        return redirect(url_for('cart'))
    else:
        return redirect(url_for('wishlist'))

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

@app.route('/product_not_found')
def product_not_found():
    return make_response(render_template('product-not-found.html'), headers)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)