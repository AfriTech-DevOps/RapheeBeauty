# # from app import db
# from app import *
from flask_login import UserMixin, LoginManager
# from flask import current_app
# from flask_admin.contrib.sqla import ModelView
# from flask_admin.form import SecureForm
# from werkzeug.utils import secure_filename
# from datetime import datetime


# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = 'login'

# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(user_id)

# class User(UserMixin, db.Model):
#     id = db.Column(db.Integer, primary_key = True)
#     full_name = db.Column(db.String(255), nullable = False)
#     email = db.Column(db.String(255), nullable = False, unique=True)
#     password = db.Column(db.String(255), nullable = False)
#     is_superuser = db.Column(db.Boolean, nullable = False)
#     created_at = db.Column(db.String(16), default=datetime.now().strftime('%d-%m-%Y %H:%M'))
#     reviews = db.relationship('Review', backref = 'user')

#     def _init_(self, full_name, email, password, is_superuser):
#         self.full_name = full_name
#         self.email = email
#         self.password = password
#         self.is_superuser = is_superuser

#     def save(self):
#         db.session.add(self)
#         db.session.commit()

# class Contact(db.Model):
#     id = db.Column(db.Integer, primary_key = True)
#     full_name = db.Column(db.String(255), nullable = False)
#     email = db.Column(db.String(255), nullable = False)
#     subject = db.Column(db.String(255), nullable = False)
#     message = db.Column(db.Text, nullable = False)
#     created_at = db.Column(db.String(16), default=datetime.now().strftime('%d-%m-%Y %H:%M'))

#     def _init_(self, full_name, email, subject, message):
#         self.full_name = full_name
#         self.email = email
#         self.subject = subject 
#         self.message = message

#     def save(self):
#         db.session.add(self)
#         db.session.commit()

# class Newsletter(db.Model):
#     id = db.Column(db.Integer, primary_key = True)
#     full_name = db.Column(db.String(100), nullable = False)
#     email = db.Column(db.String(100), nullable = False, unique=True)
#     created_at = db.Column(db.String(16), default=datetime.now().strftime('%d-%m-%Y %H:%M'))
    
#     def _init_(self, full_name, email):
#         self.full_name = full_name
#         self.email = email

#     def save(self):
#         db.session.add(self)
#         db.session.commit()

# class Category(db.Model):
#     id = db.Column(db.Integer, primary_key = True)
#     name = db.Column(db.String(30), nullable = False)
#     parent_id = db.Column(db.Integer, db.ForeignKey('category.id', ondelete='CASCADE'))
#     category_rels = db.relationship('Categoryproductrel', backref = 'category')
#     parents = db.relationship('Category', remote_side=id, backref='sub_category')

#     def _init_(self, name, parent_id):
#         self.name = name
#         self.parent_id = parent_id

#     def save(self):
#         db.session.add(self)
#         db.session.commit()

# class Product(db.Model):
#     id = db.Column(db.Integer, primary_key = True)
#     name = db.Column(db.String(30), nullable = False)
#     price = db.Column(db.Numeric(precision=10, scale=2, asdecimal=False, decimal_return_scale=None), nullable = False)
#     description = db.Column(db.Text, nullable = False)
#     category_rels = db.relationship('Categoryproductrel', backref = 'product')
#     cover_image = db.Column(db.String(200), nullable = False)
#     favorites = db.relationship('Favorites', backref = 'product')

#     def _init_(self, name, price, description, cover_image):
#         self.name = name
#         self.price = price
#         self.description = description
#         self.cover_image = cover_image
    

#     def save(self):
#         db.session.add(self)
#         db.session.commit()

# class Categoryproductrel(db.Model):
#     id = db.Column(db.Integer, primary_key = True)
#     product_id = db.Column(db.Integer, db.ForeignKey('product.id', ondelete='CASCADE'))
#     category_id = db.Column(db.Integer, db.ForeignKey('category.id', ondelete='CASCADE'))

#     def _init_(self, product_id, category_id):
#         self.product_id = product_id
#         self.category_id = category_id

#     def save(self):
#         db.session.add(self)
#         db.session.commit()

# class Image(db.Model):
#     id = db.Column(db.Integer, primary_key = True)
#     image = db.Column(db.String(50), nullable = False)
#     product_id = db.Column(db.Integer, db.ForeignKey('product.id', ondelete='CASCADE')) 

#     def _init_(self, image, product_id):
#         self.image = image
#         self.product_id = product_id

#     def save(self):
#         db.session.add(self)
#         db.session.commit()

# class Review(db.Model):
#     id = db.Column(db.Integer, primary_key = True)
#     content = db.Column(db.Text, nullable = False)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
#     product_id = db.Column(db.Integer, db.ForeignKey('product.id', ondelete='CASCADE'))
#     created_at = db.Column(db.String(16), default=datetime.now().strftime('%d-%m-%Y %H:%M'))

#     def _init_(self, content, user_id, product_id):
#         self.content = content
#         self.user_id = user_id
#         self.product_id = product_id

#     def save(self):
#         db.session.add(self)
#         db.session.commit()

# class Favorites(db.Model):
#     id = db.Column(db.Integer, primary_key = True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
#     product_id = db.Column(db.Integer, db.ForeignKey('product.id', ondelete='CASCADE'))
#     created_at = db.Column(db.String(16), default=datetime.now().strftime('%d-%m-%Y %H:%M'))

#     def _init_(self, user_id, product_id):
#         self.user_id = user_id
#         self.product_id = product_id

#     def save(self):
#         db.session.add(self)
#         db.session.commit()

# class Discounts(db.Model):
#     id = db.Column(db.Integer, primary_key = True)
#     percent = db.Column(db.Integer, nullable = False)
#     product_id = db.Column(db.Integer, db.ForeignKey('product.id', ondelete='CASCADE'), unique=True)
#     created_at = db.Column(db.String(16), default=datetime.now().strftime('%d-%m-%Y %H:%M'))
    
#     def _init_(self, percent, product_id):
#         self.percent = percent
#         self.product_id = product_id

#     def save(self):
        
#         db.session.add(self)
#         db.session.commit()



class User(UserMixin):
    def __init__(self, id, full_name, email, password, is_superuser):
        self.id = id
        self.full_name = full_name
        self.email = email
        self.password = password
        self.is_superuser = is_superuser

    def is_active(self):
        return True
    
    def is_authenticated(self):
        return True
    
    def is_anonymous(self):
        return False