from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://{user}:{password}@{server}/{database}'.format(user='root', password='mayank14', server='127.0.0.1:5000', database='mysqldb')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='emp', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    emp_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    def __repr__(self):
        return f"Post('{self.author_id}', '{self.date_posted}')"

posts = [
    {
        'author': 'josh',
        'emp': 'mac',
        'points': 100,
        'tags': ['Innovation', 'TeamWork'],
        'content': 'lorem ipsum',
        'date_posted': 'Aug 4, 2009'
    },
    {
        'author': 'Ellie',
        'emp': 'Christine',
        'points': 400,
        'tags': ['Ambition', 'TeamWork'],
        'content': 'lorem ipsum blah blah',
        'date_posted': 'Jan 16, 2024'
    }
]

details = [
    {
        'user': 'mac',
        'points': 1000
    },
    {
        'user': 'lary',
        'points': 800
    },
    {
        'user': 'Josh',
        'points': 600
    }
]

@app.route("/")
@app.route("/login", methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route("/home")
def home():
    return render_template('home.html', posts = posts)

@app.route("/new_blog")
def new_blog():
    return render_template('new_blog.html', title = 'New Post')

@app.route("/leaderboard")
def leaderboard():
    return render_template('leaderboard.html', title = 'leaderboard', len = len(details), details = details)

if __name__ == '__main__':
    app.run(debug=True)