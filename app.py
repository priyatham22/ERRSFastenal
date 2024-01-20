from flask import Flask, render_template, request, redirect, session, url_for,jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import aliased
from sqlalchemy import func,update,select
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:mayank14@localhost/sys'
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
    curr_points = db.Column(db.Integer, default=0) 

class Post(db.Model):
    __tablename__ = 'Posts'  
    post_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    points = db.Column(db.Integer, nullable=False, default=0) 
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    user = db.relationship('User', backref='posts')

class Likes(db.Model):
    __tablename__ = 'likes'  
    user_id = db.Column(db.Integer, db.ForeignKey('Posts.post_id'),primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'),primary_key=True)



@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html',title='Home')

@app.route("/feed")
def feed():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    manager_alias = aliased(User, name="manager")

    subquery = (
        db.session.query(Likes.post_id)
        .filter(
            Likes.post_id == Post.post_id,
            Likes.user_id == session["user_id"],
        )
        .exists()
    )

    query = (
        db.session.query(
            User.username.label("user_name"),
            manager_alias.username.label("manager_name"),
            func.date_format(Post.timestamp,'%d/%m/%Y').label('timestamp'),
            Post.post_id,
            Post.content,
            Post.category,
            Post.points,
            subquery.label("liked"),
        )
        .join(manager_alias, User.manager_id == manager_alias.user_id)
        .join(Post, User.user_id == Post.user_id)
        .order_by(Post.timestamp.desc())
    )

    result = query.all()
    return render_template('feed.html', posts=result, session = session,len=len(result))

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
            return redirect(url_for('feed'))
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

        return redirect(url_for('feed'))

    else:

        manager_id = session['user_id'] 
        employees = User.query.filter_by(manager_id=manager_id).all()

        employee_choices = [(employee.user_id, f"{employee.name} ({employee.user_id})") for employee in employees]
        return render_template('new_blog.html', title = 'New Post', employee_choices=employee_choices)

@app.route("/leaderboard")
def leaderboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    details = User.query.with_entities(User.username, User.points).order_by(User.points.desc()).all()
    return render_template('leaderboard.html', title = 'leaderboard', len = len(details), details = details)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route("/likefunction",methods=['POST'])
def likefunction():
    post_id=request.json.get("post_id")
    liked=request.json.get("liked")

    def update_points(x,post_id):
        subquery = (
                select(Post.user_id)
                .where(Post.post_id == post_id) 
                .alias('subquery')
            )

        update_user_points = (
            update(User)
            .values(curr_points=User.curr_points +x, points=User.points + x)
            .where(User.user_id.in_(subquery))
        )

        update_post_points = (
            update(Post)
            .values(points=Post.points +x)
            .where(Post.post_id == post_id)
        )

        db.session.execute(update_post_points)
        db.session.execute(update_user_points)
        db.session.commit()
        
    if liked:
        new_likepost = Likes(user_id=session["user_id"], post_id=post_id)
        db.session.add(new_likepost)
        db.session.commit()
            #updating points
        update_points(5,post_id)

    else:
        # deleting the 
        db.session.query(Likes).filter_by(post_id=post_id, user_id=session["user_id"]).delete()
        db.session.commit()
            #updating points
        update_points(-5,post_id)
        return jsonify({'update': True})
        
    return jsonify({'error': "got error"})
    

if __name__ == '__main__':
    app.run(debug=True)
