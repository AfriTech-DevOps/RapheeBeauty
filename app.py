from flask import Flask, render_template, request, redirect, url_for, flash, make_response, blueprints, jsonify, Response, send_file, g, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
# from werkzeug.security import generate_password_hash, check_password_hash
from passlib.hash import sha256_crypt
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, PasswordField, BooleanField, SubmitField, TextAreaField, IntegerField, FileField, RadioField, SelectMultipleField, widgets
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
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
import secrets
import redis
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

load_dotenv()

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(CURRENT_DIR, 'static')
IMAGE_DIR = os.path.join(STATIC_DIR, 'assets/uploads/images')

if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

app = Flask(__name__)
CORS(app)
# Session(app)
# sess = Session()
# token = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz1234567890', 32))
token = secrets.token_hex(64)
app.secret_key = token
app.config['SESSION_TYPE'] = 'redis'
# app.config['SESSION_REDIS'] = redis.from_url(os.getenv('REDIS_URL'))
app.config['SESSION_REDIS'] = redis.from_url('redis://216.80.104.71:6379')
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = False
# app.config['SECRET_KEY'] = secrets.token_hex(32)
# app.config['SESSION_COOKIE_HTTPONLY'] = False
# app.config['SESSION_COOKIE_SAMESITE'] = 'None'
# app.config['SESSION_COOKIE_SECURE'] = True
# app.config['SESSION_COOKIE_DOMAIN'] = '.rapheebeauty.com'
# app.config['PERMANENT_SESSION_LIFETIME'] = 3600
# app.config['SESSION_REFRESH_EACH_REQUEST'] = True
# app.config['SESSION_COOKIE_PATH'] = '/'
app.config['FLASK_ENV'] = 'development'
app.config['DEBUG'] = True
app.config['TESTING'] = True
app.config['FLASK_APP'] = 'app.py'
app.config['UPLOAD_FOLDER'] = IMAGE_DIR
ALLOWED_EXTENSIONS = {'png', 'svg', 'jpg'}
# app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}:3306/{os.getenv('MYSQL_DATABASE')}"

server_session = Session(app)
# session = {}

config = {
    'host': os.getenv('MYSQL_HOST'),
    'port': 3306,
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DATABASE')
}


# def get_db_connection():
#     conn = sql.connect('rapheeBeauty-database.db', check_same_thread=False)
#     return conn
#     # with app.app_context():
#     #     if 'db_connection' not in g:
#     #         g.db_connection = mysql.connect(**config)
#     #     return g.db_connection


def get_db_connection():
    try:
        conn = mysql.connect(**config)
        return conn
    except Error as e:
        return "<html><body><h1>500 Internal Server Error</h1></body></html>"

database.create_database(get_db_connection())
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
    "Authorization": "Bearer " + token
    # "Session-Cookie-Domain": app.config['SESSION_COOKIE_DOMAIN'],
    # "Session-Cookie-Path": app.config['SESSION_COOKIE_PATH'],
    # "Session-Cookie-Secure": app.config['SESSION_COOKIE_SECURE'],
    # "Session-Cookie-HttpOnly": app.config['SESSION_COOKIE_HTTPONLY'],
    # "Session-Cookie-SameSite": app.config['SESSION_COOKIE_SAMESITE'],
    # "Session-Cookie-Name": app.config['SESSION_COOKIE_NAME']
}

requests_total = Counter('http_requests_total', 'Total HTTP Requests (count)', ['method', 'endpoint'])

class ProductCat(FlaskForm):
    product_cats = SelectField('Gender', choices=['Select Category', 'Fragrance', 'Skincare', 'Makeup', 'Hair', 'Bodycare'])

class AddProduct(FlaskForm):
    product_name = StringField('Product Name', validators=[DataRequired(), Length(min=2, max=50)])
    product_price = StringField('Product Price', validators=[DataRequired()])
    product_discount_price = StringField('Product Discount Price', validators=[DataRequired()])
    product_image = FileField('Product Image', validators=[DataRequired()])
    product_category = SelectField('Product Category', choices=['Fragrance', 'Skincare', 'Makeup', 'Hair', 'Bodycare'])
    product_reviews = StringField('Product Reviews', validators=[DataRequired()])
    submit = SubmitField('Add Product')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session and session['logged_in'] and session['current_user']:
            print("User is logged in")
            return f(*args, **kwargs)
        else:
            flash("You need to login for access")
            return redirect(url_for('login'))
    return wrap

def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'is_superuser' in session and session['is_superuser']:
            print("User is admin")
            return f(*args, **kwargs)
        else:
            flash("You need to login as admin for access")
            return redirect(url_for('login'))
    return wrap

# @app.errorhandler(404)
# @app.route('/error')
# def error_page():
#     return make_response(render_template('404.html'), headers)

@app.route('/login', methods=['GET', 'POST'])
def login():
    requests_total.labels('GET', '/login').inc()
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        email = request.form.get('email').lower()
        password = request.form.get('tp_password')
        with app.app_context():
            cursor.execute(f"SELECT * FROM customer WHERE email = '{email}'")
            customer = cursor.fetchone()
            # print(customer)
            if customer and sha256_crypt.verify(password, customer[3]):
                print("Password matched")
                session['logged_in'] = True
                session['email'] = customer[2]
                session['id'] = customer[0]
                session['current_user'] = customer[1]  # Set current_user here
                session['is_superuser'] = customer[4]
                session['cookie'] = token
                headers['SESSIONID'] = f"{session['cookie']}-{session['id']}-{session['email']}"
                if not session['is_superuser']:
                    return redirect(url_for('profile'))
                else:
                    return redirect(url_for('admin_items'))
            else:
                flash('Invalid Credentials.', 'danger')
                return redirect(request.referrer)
    else:
        if 'logged_in' in session and session['logged_in']:
            if not session['is_superuser']:
                return redirect(url_for('profile'))
            else:
                return redirect(url_for('admin_items'))
        return make_response(render_template('login.html'), headers)



@app.route('/register', methods=['GET', 'POST'])
def register():
    requests_total.labels('GET', '/register').inc()
    conn = get_db_connection()
    if request.method == 'POST':
        full_name = request.form.get('name')
        email = request.form.get('email').lower()
        password = request.form.get('tp_password')

        print(f"full_name: {full_name}, email: {email}, password: {password}")
        get_customer = database.get_customer_by_email(conn, email)
        if get_customer:
            flash('Customer already exists.', 'danger')
            return redirect(url_for('register'))
        with app.app_context():
            database.insert_customer_data(conn, full_name, email, sha256_crypt.encrypt(password), False)
            return redirect(url_for('login'))
    
    else:
        return make_response(render_template('register.html'), headers)


@app.route('/logout')
@login_required
def logout():
    requests_total.labels('GET', '/logout').inc()
    session.pop('logged_in', None)
    session.pop('email', None)
    session.pop('id', None)
    session.pop('current_user', None)
    session.pop('is_superuser', None)
    session.pop('cookie', None)

    r = redis.StrictRedis(host=os.getenv('LOCALHOST'), port=os.getenv('REDIS_PORT'), db=os.getenv('REDIS_DB'))
    print(f"session:{str(session.sid)}")
    r.delete(session.sid)
    print("Session deleted from redis")

    flash('Logged out successfully.', 'success')
    return redirect(request.referrer)


@app.route('/admin')
# @login_required
def admin():
    requests_total.labels('GET', '/admin').inc()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    return make_response(render_template('admin.html', products=products), headers)

@admin_required
@app.route('/admin_items', methods=['GET', 'POST'])
def admin_items():
    requests_total.labels('GET', '/admin_items').inc()
    conn = get_db_connection()
    cursor = conn.cursor()


    page = request.args.get('page', 1, type=int)
    per_page = 10
    cursor.execute("SELECT COUNT(*) FROM products")
    total_count = cursor.fetchone()[0]

    num_pages = total_count // per_page + (total_count % per_page > 0)
    offset = (page - 1) * per_page

    cursor.execute(f"SELECT * FROM products LIMIT {per_page} OFFSET {offset}")
    products = cursor.fetchall()
    
    return make_response(render_template('admin_items.html', products=products, page=page, per_page=per_page, num_pages=num_pages), headers)

@admin_required
@app.route('/admin_add_item', methods=['GET', 'POST'])
def admin_add_item():
    requests_total.labels('GET', '/admin_add_item').inc()
    conn = get_db_connection()
    cursor = conn.cursor()
    form = AddProduct()


    if request.method == 'POST':
        product_name = form.product_name.data
        product_price = form.product_price.data
        product_discount_price = form.product_discount_price.data
        product_image = request.files['product_img']
        product_category = form.product_category.data
        product_reviews = form.product_reviews.data
        print(product_name, product_price, product_discount_price, product_image, product_category, product_reviews)
        

        with app.app_context():
            if product_image == '':
                flash('Please upload an image.', 'danger')
                return redirect(url_for('admin_add_item'))
            
            if product_image and allowed_file(product_image.filename):
                filename = secure_filename(product_image.filename)
                product_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image = url_for('static', filename=f"assets/uploads/images/{filename}")
                print(image)

            database.insert_product_data(conn, product_name, product_price, product_discount_price, image, product_category, product_reviews)
            flash('Product added successfully.', 'success')
            return redirect(url_for('admin_items'))
    else:
        return make_response(render_template('admin_add_item.html', form=form), headers)

@admin_required
@app.route('/admin_edit_item/<int:product_id>', methods=['GET', 'POST'])
def admin_edit_item(product_id):
    requests_total.labels('GET', '/admin_edit_item').inc()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM products WHERE product_id={product_id}")
    product = cursor.fetchone()
    print(product)
    form = AddProduct()
    if request.method == 'POST':
        product_name = form.product_name.data
        product_price = form.product_price.data
        product_discount_price = form.product_discount_price.data
        product_image = form.product_image.data
        product_category = form.product_category.data
        product_reviews = form.product_reviews.data
        print(product_name, product_price, product_discount_price, product_image, product_category, product_reviews)
        with app.app_context():
            database.update_product_data(conn, product_id, product_name, product_price, product_discount_price, product_image, product_category, product_reviews)
            flash('Product updated successfully.', 'success')
            return redirect(url_for('admin_items'))
    else:
        return make_response(render_template('admin_edit_item.html', product=product), headers)
@admin_required
@app.route('/admin_delete_item/<int:product_id>', methods=['GET', 'POST'])
def admin_delete_item(product_id):
    requests_total.labels('GET', '/admin_delete_item').inc()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM products WHERE product_id={product_id}")
    conn.commit()
    flash('Product deleted successfully.', 'success')
    return redirect(url_for('admin_items'))

# @app.route('/items')
# def admin_items():
#     return make_response(render_template('admin_items.html'), headers)
@app.route('/home')
@app.route('/' , methods=['GET', 'POST'])
def index():
    requests_total.labels('GET', '/').inc()
    conn = get_db_connection()
    cursor = conn.cursor()
    random_products_query = """SELECT * FROM products ORDER BY RAND() LIMIT 8"""
    cursor.execute(random_products_query)
    random_products = cursor.fetchall()
    print(random_products)


    product_cats = ['Select Category', 'Fragrance', 'Skincare', 'Makeup', 'Haircare', 'Bodycare']
    product_cats_form = ProductCat()
    selected_cat = ''


    fragrance_count_query = """SELECT COUNT(*) FROM products WHERE category='fragrance'"""
    skincare_count_query = """SELECT COUNT(*) FROM products WHERE category='skincare'"""
    makeup_count_query = """SELECT COUNT(*) FROM products WHERE category='makeup'"""
    haircare_count_query = """SELECT COUNT(*) FROM products WHERE category='hair'"""
    bodycare_count_query = """SELECT COUNT(*) FROM products WHERE category='bodycare'"""

    cursor.execute(fragrance_count_query)
    data = cursor.fetchall()[0]
    print(str(data[0]))

    cursor.execute(fragrance_count_query)
    fragrance_count = cursor.fetchone()[0]
    cursor.execute(skincare_count_query)
    skincare_count = cursor.fetchone()[0]
    cursor.execute(makeup_count_query)
    makeup_count = cursor.fetchone()[0]
    cursor.execute(haircare_count_query)
    haircare_count = cursor.fetchone()[0]
    cursor.execute(bodycare_count_query)
    bodycare_count = cursor.fetchone()[0]

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

    if 'logged_in' not in session:
        wishlist_count = 0
        cart_count = 0
    else:
        wishlist_query = f"""SELECT COUNT(*) FROM wishlist where customer_id = {session['id']}"""
        cursor.execute(wishlist_query)
        wishlist_count = cursor.fetchone()[0]

        cart_query = f"""SELECT COUNT(*) FROM cart where customer_id = {session['id']}"""
        cursor.execute(cart_query)
        cart_count = cursor.fetchone()[0]



    if selected_cat == 'Select Category' or selected_cat == 'Fragrances' or selected_cat == 'Skincare' or selected_cat == 'Makeup' or selected_cat == 'Haircare' or selected_cat == 'Bodycare' or selected_cat == 'Accessories' or selected_cat == 'Gifts' or selected_cat == 'Brands':
        return make_response(render_template('index.html', product_cats_form=product_cats_form, product_cats=product_cats, selected_cat=selected_cat, 
                                             random_products=random_products, fragrance_count=fragrance_count, skincare_count=skincare_count, makeup_count=makeup_count,
                                             haircare_count=haircare_count, bodycare_count=bodycare_count, categories=categories, wishlist_count=wishlist_count, cart_count=cart_count), headers)
    return make_response(render_template('index.html', product_cats_form=product_cats_form, product_cats=product_cats, random_products=random_products, fragrance_count=fragrance_count, 
                                         skincare_count=skincare_count, makeup_count=makeup_count,
                                             haircare_count=haircare_count, bodycare_count=bodycare_count, categories=categories, wishlist_count=wishlist_count, cart_count=cart_count), headers)

@app.route('/contact')
def contact():
    requests_total.labels('GET', '/contact').inc()
    conn = get_db_connection()
    cursor = conn.cursor()
    if 'logged_in' not in session:
        wishlist_count = 0
        cart_count = 0
    else:
        wishlist_query = f"""SELECT COUNT(*) FROM wishlist where customer_id = {session['id']}"""
        cursor.execute(wishlist_query)
        wishlist_count = cursor.fetchone()[0]

        cart_query = f"""SELECT COUNT(*) FROM cart where customer_id = {session['id']}"""
        cursor.execute(cart_query)
        cart_count = cursor.fetchone()[0]

    return make_response(render_template('contact.html', wishlist_count=wishlist_count, cart_count=cart_count), headers)

@app.route('/shop')
def shop():
    requests_total.labels('GET', '/shop').inc()
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

    
    

    cursor.execute(fragrance_count_query)
    fragrance_count = cursor.fetchone()[0]
    cursor.execute(skincare_count_query)
    skincare_count = cursor.fetchone()[0]
    cursor.execute(makeup_count_query)
    makeup_count = cursor.fetchone()[0]
    cursor.execute(haircare_count_query)
    haircare_count = cursor.fetchone()[0]
    cursor.execute(bodycare_count_query)
    bodycare_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM products")
    total_count = cursor.fetchone()[0]

    num_pages = total_count // per_page + (total_count % per_page > 0)
    offset = (page - 1) * per_page

    # all_products_query = """SELECT * FROM products LIMIT ? ORDER BY RAND()"""
    cursor.execute(f"SELECT * FROM products ORDER BY RAND() LIMIT {per_page} OFFSET {offset}")
    products = cursor.fetchall()
    # print(products)

    if 'logged_in' not in session:
        wishlist_count = 0
        cart_count = 0
    else:
        wishlist_query = f"""SELECT COUNT(*) FROM wishlist where customer_id = {session['id']}"""
        cursor.execute(wishlist_query)
        wishlist_count = cursor.fetchone()[0]

        cart_query = f"""SELECT COUNT(*) FROM cart where customer_id = {session['id']}"""
        cursor.execute(cart_query)
        cart_count = cursor.fetchone()[0]

    conn.close()
    return make_response(render_template('shop.html', fragrance_count=fragrance_count, skincare_count=skincare_count, makeup_count=makeup_count,
                                             haircare_count=haircare_count, bodycare_count=bodycare_count, products=products, page=page, num_pages=num_pages, 
                                             per_page=per_page, categories=categories, wishlist_count=wishlist_count, cart_count=cart_count), headers)


@app.route('/category/<string:category>')
def category(category):
    requests_total.labels('GET', '/category').inc()
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
        cursor.execute(f"SELECT * FROM products WHERE category='{category}' ORDER BY RAND() LIMIT ? OFFSET ?", (per_page, offset))
        products = cursor.fetchall()
        print(products)
        conn.close()
        return make_response(render_template('shop-category.html', products=products, category=category, page=page, num_pages=num_pages, per_page=per_page), headers)

@app.route('/search', methods=['GET', 'POST'])
def search():
    requests_total.labels('GET', '/search').inc()
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

    cursor.execute(fragrance_count_query)
    fragrance_count = cursor.fetchone()[0]
    cursor.execute(skincare_count_query)
    skincare_count = cursor.fetchone()[0]
    cursor.execute(makeup_count_query)
    makeup_count = cursor.fetchone()[0]
    cursor.execute(haircare_count_query)
    haircare_count = cursor.fetchone()[0]
    cursor.execute(bodycare_count_query)
    bodycare_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM products")
    total_count = cursor.fetchone()[0]

    num_pages = total_count // per_page + (total_count % per_page > 0)
    offset = (page - 1) * per_page

    # all_products_query = """SELECT * FROM products LIMIT ? ORDER BY RAND()"""
    cursor.execute(f"SELECT * FROM products ORDER BY RAND() LIMIT {per_page} OFFSET {offset}")
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
    
    if 'logged_in' not in session:
        wishlist_count = 0
        cart_count = 0
    else:
        wishlist_query = f"""SELECT COUNT(*) FROM wishlist where customer_id = {session['id']}"""
        cursor.execute(wishlist_query)
        wishlist_count = cursor.fetchone()[0]

        cart_query = f"""SELECT COUNT(*) FROM cart where customer_id = {session['id']}"""
        cursor.execute(cart_query)
        cart_count = cursor.fetchone()[0]

         
    return make_response(render_template('shop-list.html', query=query, category=category, categories=categories, fragrance_count=fragrance_count, skincare_count=skincare_count, makeup_count=makeup_count,
                                             haircare_count=haircare_count, bodycare_count=bodycare_count, products=products, page=page, num_pages=num_pages, per_page=per_page, wishlist_count=wishlist_count, cart_count=cart_count), headers)

    
@app.route('/shop_list')
def shop_list():
    requests_total.labels('GET', '/shop_list').inc()

    return make_response(render_template('shop-list.html'), headers)

@app.route('/about')
def about():
    requests_total.labels('GET', '/about').inc()
    conn = get_db_connection()
    cursor = conn.cursor()
    if 'logged_in' not in session:
        wishlist_count = 0
        cart_count = 0
    else:
        wishlist_query = f"""SELECT COUNT(*) FROM wishlist where customer_id = {session['id']}"""
        cursor.execute(wishlist_query)
        wishlist_count = cursor.fetchone()[0]

        cart_query = f"""SELECT COUNT(*) FROM cart where customer_id = {session['id']}"""
        cursor.execute(cart_query)
        cart_count = cursor.fetchone()[0]
    return make_response(render_template('about.html', wishlist_count=wishlist_count, cart_count=cart_count), headers)

@login_required
@app.route('/wishlist')
def wishlist():
    requests_total.labels('GET', '/wishlist').inc()
    conn = get_db_connection()
    cursor = conn.cursor()
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    try:
        cursor.execute(f"Select id from customer where email='{session['email']}'")
        customer_id = cursor.fetchone()[0]
        cursor.execute(f"SELECT * FROM wishlist WHERE customer_id='{customer_id}'")
        wishlist = cursor.fetchall()
        # print(wishlist)

        # if not wishlist:
        #     return make_response(render_template('wishlist.html', products=[]), headers)
        
        products = []
        for item in wishlist:
            # print(item[1])
            cursor.execute(f"SELECT * FROM products WHERE product_id={item[1]}")
            product = cursor.fetchone()
            if product:
                products.append(product)
            
        # print(products)
        
        return make_response(render_template('wishlist.html', products=products, wishlist=wishlist), headers)
    except Exception as e:
        print(e)
        return make_response(render_template('wishlist.html', products=[]), headers)
    

# @login_required
@app.route('/profile')
@login_required
def profile():
    try:
        requests_total.labels('GET', '/profile').inc()
        conn = get_db_connection()
        cursor = conn.cursor()
        user = session['current_user']
        wishlist_query = """SELECT COUNT(*) FROM wishlist"""
        cursor.execute(wishlist_query)
        wishlist_count = cursor.fetchone()[0]
        cart_query = """SELECT COUNT(*) FROM cart"""
        cursor.execute(cart_query)
        cart_count = cursor.fetchone()[0]
        with app.app_context():
            return make_response(render_template('profile.html', user=user, wishlist_count=wishlist_count, cart_count=cart_count), headers)
    except Exception as e:
        print(e)
        return redirect(url_for('login'))
@app.route('/cart')
def cart():
    requests_total.labels('GET', '/cart').inc()
    conn = get_db_connection()
    cursor = conn.cursor()
    if 'email' not in session:
        return redirect(url_for('login'))
    else:
        cursor.execute(f"Select id from customer where email='{session['email']}'")
        customer_id = cursor.fetchone()[0]
        cursor.execute(f"SELECT * FROM cart WHERE customer_id={customer_id}")
        cart = cursor.fetchall()
        # print(cart)

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
        # print(products)

        wishlist_query = """SELECT COUNT(*) FROM wishlist"""
        cursor.execute(wishlist_query)
        wishlist_count = cursor.fetchone()[0]

        cart_query = """SELECT COUNT(*) FROM cart"""
        cursor.execute(cart_query)
        cart_count = cursor.fetchone()[0]
        
        return make_response(render_template('cart.html', products=products, total=total, subtotal=subtotal, wishlist_count=wishlist_count, cart_count=cart_count), headers)


@app.route('/coupon')
def coupon():
    requests_total.labels('GET', '/coupon').inc()
    conn = get_db_connection()
    cursor = conn.cursor()

    if 'logged_in' not in session:
        wishlist_count = 0
        cart_count = 0
    else:
        wishlist_query = f"""SELECT COUNT(*) FROM wishlist where customer_id = {session['id']}"""
        cursor.execute(wishlist_query)
        wishlist_count = cursor.fetchone()[0]

        cart_query = f"""SELECT COUNT(*) FROM cart where customer_id = {session['id']}"""
        cursor.execute(cart_query)
        cart_count = cursor.fetchone()[0]
    return make_response(render_template('coupon.html', wishlist_count=wishlist_count, cart_count=cart_count), headers)

@app.route('/checkout')
def checkout():
    requests_total.labels('GET', '/checkout').inc()
    return make_response(render_template('checkout.html'), headers)

@app.route('/product_details')
def product_details():
    requests_total.labels('GET', '/product_details').inc()
    return make_response(render_template('product-details.html'), headers)

@app.route('/product_details_countdown')
def product_details_countdown():
    requests_total.labels('GET', '/product_details_countdown').inc()
    return make_response(render_template('product-details-countdown.html'), headers)

@app.route('/product_details_gallery')
def product_details_gallery():
    requests_total.labels('GET', '/product_details_gallery').inc()
    return make_response(render_template('product-details-gallery.html'), headers)

@app.route('/product_details_progress')
def product_details_progress():
    requests_total.labels('GET', '/product_details_progress').inc()
    return make_response(render_template('product-details-progress.html'), headers)

@app.route('/product_details_swatches')
def product_details_swatches():
    requests_total.labels('GET', '/product_details_swatches').inc()
    return make_response(render_template('product-details-swatches.html'), headers)

@app.route('/product_details_list')
def product_details_list():
    requests_total.labels('GET', '/product_details_list').inc()
    return make_response(render_template('product-details-list.html'), headers)

@app.route('/compare')
def compare():
    requests_total.labels('GET', '/compare').inc()
    conn = get_db_connection()
    cursor = conn.cursor()

    if 'logged_in' not in session:
        wishlist_count = 0
        cart_count = 0
    else:
        wishlist_query = f"""SELECT COUNT(*) FROM wishlist where customer_id = {session['id']}"""
        cursor.execute(wishlist_query)
        wishlist_count = cursor.fetchone()[0]

        cart_query = f"""SELECT COUNT(*) FROM cart where customer_id = {session['id']}"""
        cursor.execute(cart_query)
    return make_response(render_template('compare.html', wishlist_count=wishlist_count, cart_count=cart_count), headers)

@app.route('/404')
def error():
    requests_total.labels('GET', '/404').inc()
    return make_response(render_template('404.html'), headers)

@app.route('/forgot_password')
def forgot():
    requests_total.labels('GET', '/forgot_password').inc()
    return make_response(render_template('forgot.html'), headers)

@app.route('/orders')
@login_required
def order():
    requests_total.labels('GET', '/orders').inc()
    return make_response(render_template('order.html'), headers)

@app.route('/shop_category')
def shop_category():
    requests_total.labels('GET', '/shop_category').inc()
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
    # print(product_cat)

    if 'logged_in' not in session:
        wishlist_count = 0
        cart_count = 0
    else:
        wishlist_query = f"""SELECT COUNT(*) FROM wishlist where customer_id = {session['id']}"""
        cursor.execute(wishlist_query)
        wishlist_count = cursor.fetchone()[0]

        cart_query = f"""SELECT COUNT(*) FROM cart where customer_id = {session['id']}"""
        cursor.execute(cart_query)
        cart_count = cursor.fetchone()[0]

    return make_response(render_template('shop-category.html', product_cat=product_cat, wishlist_count=wishlist_count, cart_count=cart_count), headers)


@app.route('/addToCart/<int:product_id>', methods=['GET', 'POST'])
def add_to_cart(product_id):
    requests_total.labels('GET', '/addToCart').inc()
    conn = get_db_connection()
    cursor = conn.cursor()
    quantity = 1
    if 'email' not in session:
        return redirect(url_for('login'))
    else:
        # product_id = request.args.get('product_id')
        cursor.execute(f"Select id from customer where email='{session['email']}'")
        customer_id = cursor.fetchone()[0]
        
        # Check if product is already in cart
        cursor.execute(f"SELECT * FROM cart WHERE product_id={product_id} AND customer_id={customer_id}")
        existing_cart_item = cursor.fetchone()
        print(existing_cart_item)

        if 'ShoppingCart' not in session:
            session['ShoppingCart'] = []
        

        if existing_cart_item:
            new_quantity = existing_cart_item[3] + quantity
            cart_id = existing_cart_item[0]
            print(new_quantity, cart_id)
            try:
                cursor.execute(f"UPDATE cart set quantity={new_quantity} where cart_id={cart_id}")
                conn.commit()
                msg = "Added to cart successfully"
            except Error:
                conn.rollback()
                msg = "Error occured while updating cart"
        else:
            session['ShoppingCart'].append({
                'product_id': product_id,
                'quantity': quantity
            })

            try:
                cursor.execute(f"INSERT INTO cart (product_id, customer_id, quantity) VALUES ({product_id}, {customer_id}, {quantity})")
                conn.commit()
                msg = "Added to cart successfully"
            except Error:
                conn.rollback()
                msg = "Error occured while adding to cart"
    
    return redirect(url_for('cart'))

@app.route('/updateCart/<int:product_id>', methods=['GET', 'POST'])
def update_cart(product_id):
    requests_total.labels('GET', '/updateCart').inc()
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
    requests_total.labels('GET', '/removeFromCart').inc()
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

@app.route('/addToWishlist/<int:product_id>', methods=['GET', 'POST'])
def add_to_wishlist(product_id):
    requests_total.labels('GET', '/addToWishlist').inc()
    conn = get_db_connection()
    cursor = conn.cursor()
    if 'email' not in session:
        return redirect(url_for('login'))
    else:
        # product_id = request.args.get('product_id')
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
    requests_total.labels('GET', '/removeFromWishlist').inc()
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
    requests_total.labels('GET', '/addWishlistToCart').inc()
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

            cursor.execute(f"SELECT * FROM cart WHERE product_id={product_id} AND customer_id={customer_id}")
            existing_cart_item = cursor.fetchone()
            print(existing_cart_item)
            
            if existing_cart_item:
                new_quantity = existing_cart_item[3] + qty
                cart_id = existing_cart_item[0]
                print(new_quantity, cart_id)
                try:
                    cursor.execute(f"UPDATE cart set quantity={new_quantity} where cart_id={cart_id}")
                    conn.commit()
                    msg = "Added to cart successfully"
                except Error:
                    conn.rollback()
                    msg = "Error occured"
            else:
                try:
                    cursor.execute(f"INSERT INTO cart (product_id, customer_id, quantity) VALUES ({product_id}, {customer_id}, {qty})")
                    conn.commit()
                    msg = "Added to cart successfully"
                except Error:
                    conn.rollback()
                    msg = "Error occured"
        return redirect(url_for('cart'))
            
    else:
        return redirect(url_for('wishlist'))

@app.route('/shop_1600')
def shop_1600():
    requests_total.labels('GET', '/shop_1600').inc()
    return make_response(render_template('shop-1600.html'), headers)

@app.route('/shop_filter_dropdown')
def shop_filter_dropdown():
    requests_total.labels('GET', '/shop_filter_dropdown').inc()
    return make_response(render_template('shop-filter-dropdown.html'), headers)

@app.route('/shop_filter_offcanvas')
def shop_filter_offcanvas():
    requests_total.labels('GET', '/shop_filter_offcanvas').inc()
    return make_response(render_template('shop-filter-offcanvas.html'), headers)

@app.route('/shop_full_width')
def shop_full_width():
    requests_total.labels('GET', '/shop_full_width').inc()
    return make_response(render_template('shop-full-width.html'), headers)

@app.route('/shop_infinite_scroll')
def shop_infinite_scroll():
    requests_total.labels('GET', '/shop_infinite_scroll').inc()
    return make_response(render_template('shop-infinite-scroll.html'), headers)

@app.route('/shop_no_sidebar')
def shop_no_sidebar():
    requests_total.labels('GET', '/shop_no_sidebar').inc()
    return make_response(render_template('shop-no-sidebar.html'), headers)

@app.route('/shop_right_sidebar')
def shop_right_sidebar():
    requests_total.labels('GET', '/shop_right_sidebar').inc()
    return make_response(render_template('shop-right-sidebar.html'), headers)

@app.route('/shop_masonary')
def shop_masonary():
    requests_total.labels('GET', '/shop_masonary').inc()
    return make_response(render_template('shop-masonary.html'), headers)

@app.route('/404')
def error_page():
    requests_total.labels('GET', '/404').inc()
    return make_response(render_template('404.html'), headers)

@app.route('/product_not_found')
def product_not_found():
    requests_total.labels('GET', '/product_not_found').inc()
    return make_response(render_template('product-not-found.html'), headers)

@app.route('/metrics')
def metrics():
    requests_total.labels('GET', '/metrics').inc()
    return Response(generate_latest(), CONTENT_TYPE_LATEST)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)