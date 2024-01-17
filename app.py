from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:password@localhost/temp_ERP'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'secret_key'
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'Users'
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    manager_id = db.Column(db.Integer, nullable=True)
    is_manager = db.Column(db.Boolean, nullable=False, default=False)
    points = db.Column(db.Integer, default=0) 

class Post(db.Model):
    __tablename__ = 'Posts'  
    post_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    points = db.Column(db.Integer, nullable=False) 
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    user = db.relationship('User', backref='posts')

@app.route("/")
@app.route("/home")
def home():
    posts = Post.query.all()
    return render_template('home.html', posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username, password=password).first()

        if user:
            session['username'] = username
            session['user_id'] = user.user_id
            session['is_manager'] = user.is_manager
            return redirect(url_for('home'))
        else:
            return render_template('login.html', message='Invalid credentials. Please try again.')

    return render_template('login.html', message=None)

@app.route("/new_blog")
def new_blog():
    return render_template('new_blog.html', title = 'New Post')

@app.route("/leaderboard")
def leaderboard():
    details = User.query.with_entities(User.username, User.points).order_by(User.points.desc()).all()
    return render_template('leaderboard.html', title = 'leaderboard', len = len(details), details = details)

if __name__ == '__main__':
    app.run(debug=True)