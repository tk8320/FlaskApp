from application import app
from flask_sqlalchemy import SQLAlchemy
import os


#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Tejas8320@localhost/db_name'
secret_key = app.config['SECRET_KEY'] = os.urandom(128)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer,primary_key=True, index=True)
    username = db.Column(db.String(20), nullable= False, unique= True)
    password = db.Column(db.String(512), nullable= False)
    type = db.Column(db.String(10), nullable=False)
    contact_no = db.Column(db.String(10))
    count = db.Column(db.Integer, nullable=False)

    def __init__(self,uname,passwd,contact_no= -1, acc='user', count=0):
        self.username = uname
        self.password = passwd
        self.contact_no = contact_no
        self.type = acc
        self.count = count


class Courses(db.Model):
    course_id = db.Column(db.Integer, primary_key=True, index=True)
    course_name = db.Column(db.String(100), nullable=False)
    course_fee = db.Column(db.Integer, nullable=False)
    is_discount = db.Column(db.Boolean, nullable=False)
    description = db.Column(db.String(500))

    def __init__(self,name,fee,is_dis, desc=''):
        self.course_name = name
        self.course_fee = fee
        self.is_discount = is_dis
        self.description = desc


class Data(db.Model):
    name = db.Column(db.String(40), nullable= False, primary_key= True)
    age = db.Column(db.Integer, nullable= False)
    address = db.Column(db.String(100))

    def __init__(self, name, age, address= ''):
        self.name = name
        self.age = age
        self.address = address


class News(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    heading = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    likes = db.Column(db.Integer)

    def __init__(self, head, desc, name, likes=0):
        self.heading = head
        self.description = desc
        self.author = name
        self.likes = likes


