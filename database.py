import os

from dotenv import load_dotenv



load_dotenv()


def create_user_table(conn):
    cursor = conn.cursor()
    query = """CREATE TABLE IF NOT EXISTS customer(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    is_superuser BOOLEAN NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );"""
    cursor.execute(query)
    print("Customer table has been created successfully")

def create_product_table(conn):
    cursor = conn.cursor()
    query = """CREATE TABLE IF NOT EXISTS products (
	product_id INTEGER PRIMARY KEY AUTOINCREMENT,
	product_name VARCHAR(50),
	sales_price VARCHAR(50),
	discount_price VARCHAR(50),
	images VARCHAR(255),
	category VARCHAR(50),
	reviews VARCHAR(50)
    );"""
    cursor.execute(query)
    print("Product table has been created successfully")


def insert_customer_data(conn, full_name, email, password, is_superuser):
    query = """INSERT INTO customer(full_name, email, password, is_superuser) VALUES (?,?,?,?)"""
    cursor = conn.cursor()
    cursor.execute(query, (full_name,email,password,is_superuser))
    conn.commit()
    print("Customer data inserted successfully")


def insert_product_data(conn, product_name, sales_price, discount_price, images, category, reviews):
    query = """INSERT INTO products(product_name, sales_price, discount_price, images, category, reviews) VALUES (?,?,?,?,?,?)"""
    cursor = conn.cursor()
    cursor.execute(query, (product_name, sales_price, discount_price, images, category, reviews))
    conn.commit()
    print("Product data inserted successfully")

# def get_customer_by_email(conn, email):
#     cursor = conn.cursor()
#     query = """SELECT * FROM customer"""
#     cursor.execute(query)
#     result = cursor.fetchall()
#     for row in result:
#         print(row)
    

class DatabaseQuery:
    def __init__(self, conn, query, params=None):
        self.conn = conn
        self.query = query
        self.params = params
    
    def get_product_counts_by_category(self):
        cursor = self.conn.cursor()
        cursor.execute(self.query)
        result = cursor.fetchone()
        return result
    
    def get_all_products(self):
        cursor = self.conn.cursor()
        cursor.execute(self.query)
        result = cursor.fetchall()
        return result
    
    def get_product_by_id(self, product_id):
        cursor = self.conn.cursor()
        cursor.execute(self.query, (product_id,))
        result = cursor.fetchone()
        return result
