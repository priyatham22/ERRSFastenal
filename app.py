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
    points = db.Column(db.Integer, nullable=False, default=0) 
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    user = db.relationship('User', backref='posts')

@app.route("/home")
def home():
    posts = Post.query.all()
    return render_template('home.html', posts=posts, session = session)

@app.route("/register", methods=['GET', 'POST'])
def register():
    return render_template('register.html', title = 'Register')

@app.route("/")
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

    return render_template('login.html', title = 'Login', message=None)

@app.route("/new_blog", methods=['GET', 'POST'])
def new_blog():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':

        employee_id = request.form.get('employee_id')
        post_content = request.form.get('post_content')
        category = request.form.get('category')
        points = int(request.form.get('points'))

        employee = db.session.get(User, employee_id)
        if employee:
            employee.points += points
            db.session.commit()

        new_post = Post(user_id=employee_id, content=post_content, category=category, points=points)
        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for('home'))

    else:

        manager_id = session['user_id'] 
        employees = User.query.filter_by(manager_id=manager_id).all()

        employee_choices = [(employee.user_id, f"{employee.name} ({employee.user_id})") for employee in employees]
        return render_template('new_blog.html', title = 'New Post', employee_choices=employee_choices, session = session)

@app.route("/leaderboard")
def leaderboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    details = User.query.with_entities(User.username, User.points).order_by(User.points.desc()).all()
    return render_template('leaderboard.html', title = 'leaderboard', len = len(details), details = details, session = session)

if __name__ == '__main__':
    app.run(debug=True)