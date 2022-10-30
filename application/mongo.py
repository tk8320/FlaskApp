from application import app
from flask_mongoalchemy import MongoAlchemy

app.config['MONGOALCHEMY_DATABASE'] = 'newsdb'
db = MongoAlchemy(app)


class Author(db.Document):
    name = db.StringField()


class Book(db.Document):
    title = db.StringField()
    author = db.DocumentField(Author)
    year = db.IntField()