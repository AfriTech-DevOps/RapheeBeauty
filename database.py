import os

from dotenv import load_dotenv



load_dotenv()

def check_if_table_exists(conn, table_name):
    cursor = conn.cursor()
    cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
    result = cursor.fetchone()
    if result:
        return True
    else:
        return False
    

def create_database(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS rapheebeauty")
        print("Database has been created successfully")
    except Exception as e:
        print(e)


def create_user_table(conn):
    try:
        if check_if_table_exists(conn, "user"):
            print("User table already exists")
            return
        else:
            cursor = conn.cursor()
            query = """CREATE TABLE IF NOT EXISTS customer(
            id INTEGER PRIMARY KEY AUTO_INCREMENT,
            full_name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            is_superuser BOOLEAN NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );"""
            cursor.execute(query)
            print("Customer table has been created successfully")
    except Exception as e:
        print(e)

def create_product_table(conn):
    try:
        if check_if_table_exists(conn, "products"):
            print("Product table already exists")
            return
        else:
            cursor = conn.cursor()
            query = """CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTO_INCREMENT,
            product_name VARCHAR(50),
            sales_price VARCHAR(50),
            discount_price VARCHAR(50),
            images VARCHAR(255),
            category VARCHAR(50),
            reviews VARCHAR(50)
            );"""
            cursor.execute(query)
            print("Product table has been created successfully")

    except Exception as e:
        print(e)

def create_cart_table(conn):
    try:
        if check_if_table_exists(conn, "cart"):
            print("Cart table already exists")
            return
        else:
            cursor = conn.cursor()
            query = """CREATE TABLE IF NOT EXISTS cart (
            cart_id INTEGER PRIMARY KEY AUTO_INCREMENT,
            product_id INTEGER,
            customer_id INTEGER,
            quantity INTEGER,
            FOREIGN KEY(product_id) REFERENCES products(product_id),
            FOREIGN KEY(customer_id) REFERENCES customer(id)
            );"""
            cursor.execute(query)
            print("Cart table has been created successfully")
    
    except Exception as e:
        print(e)


def create_wishlist_table(conn):
    try:
        if check_if_table_exists(conn, "wishlist"):
            print("Wishlist table already exists")
            return
        else:
            cursor = conn.cursor()
            query = """CREATE TABLE IF NOT EXISTS wishlist (
            wishlist_id INTEGER PRIMARY KEY AUTO_INCREMENT,
            product_id INTEGER,
            customer_id INTEGER,
            FOREIGN KEY(product_id) REFERENCES products(product_id),
            FOREIGN KEY(customer_id) REFERENCES customer(id)
            );"""
            cursor.execute(query)
            print("Wishlist table has been created successfully")
    
    except Exception as e:
        print(e)

def insert_customer_data(conn, full_name, email, password, is_superuser):
    query = """INSERT INTO customer(full_name, email, password, is_superuser) VALUES (%s,%s,%s,%s)"""
    cursor = conn.cursor()
    cursor.execute(query, (full_name,email,password,is_superuser))
    conn.commit()
    print("Customer data inserted successfully")


def insert_product_data(conn, product_name, sales_price, discount_price, images, category, reviews):
    query = """INSERT INTO products(product_name, sales_price, discount_price, images, category, reviews) VALUES (%s,%s,%s,%s,%s,%s)"""
    cursor = conn.cursor()
    cursor.execute(query, (product_name, sales_price, discount_price, images, category, reviews))
    conn.commit()
    print("Product data inserted successfully")


def get_customer_by_email(conn, email):
    cursor = conn.cursor()
    query = f"""SELECT * FROM customer where email='{email}'"""
    cursor.execute(query)
    result = cursor.fetchone()
    
    return result

def get_product_by_category(conn, category):
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM products WHERE category = '{category}'")
    result = cursor.fetchall()
    return result
