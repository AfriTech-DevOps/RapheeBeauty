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
    )"""
    cursor.execute(query)
    print("Customer table has been created successfully")


def insert_customer_data(conn, full_name, email, password, is_superuser):
    query = """INSERT INTO customer(full_name, email, password, is_superuser) VALUES (?,?,?,?)"""
    cursor = conn.cursor()
    cursor.execute(query, (full_name,email,password,is_superuser))
    conn.commit()
    print("Customer data inserted successfully")

# def get_customer_by_email(conn, email):
#     cursor = conn.cursor()
#     query = """SELECT * FROM customer"""
#     cursor.execute(query)
#     result = cursor.fetchall()
#     for row in result:
#         print(row)