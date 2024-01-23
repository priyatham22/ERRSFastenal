from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import aliased
from sqlalchemy import func,update,select
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta
from flask_bcrypt import Bcrypt 


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:password@localhost/errp_project'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'secret_key'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    manager_id = db.Column(db.Integer, nullable=True)
    is_manager = db.Column(db.Boolean, nullable=False, default=False)
    points = db.Column(db.Integer, default=0) 
    curr_points = db.Column(db.Integer, default=0) 

class Post(db.Model):
    __tablename__ = 'posts'  
    post_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    points = db.Column(db.Integer, nullable=False, default=0) 
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    user = db.relationship('User', backref='posts')

class Request(db.Model):
    __tablename__= 'requests'
    request_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id')) 
    description = db.Column(db.String(100), nullable=False)
    values = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(15), nullable=False, default='pending')
    user = db.relationship('User', backref='requests')

class Likes(db.Model):
    __tablename__ = 'likes'  
    user_id = db.Column(db.Integer, db.ForeignKey('posts.post_id'),primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('users.user_id'),primary_key=True)

##this is in order to store the coupons generated and let the company know which coupon is valid
class Coupon(db.Model):
    __tablename__ = 'coupons'
    coupon_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    coupon_name = db.Column(db.String(20), nullable=False)
    coupon_code = db.Column(db.String(10), nullable=False)
    expiry_date=db.Column(db.Date, default=datetime.utcnow() + timedelta(days=30), nullable=False)

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

        
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
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
        
    if not session.get('is_manager', False):
        return redirect(url_for('feed'))

    if request.method == 'POST':

        employee_id = request.form.get('employee_id')
        post_content = request.form.get('post_content')
        category = request.form.get('category')
        points = int(request.form.get('points'))
        print(employee_id)
        print(post_content)
        print(category)
        print(points)

        employee = db.session.get(User, employee_id)
        
        if employee:
            employee.points += points
            employee.curr_points+=points
            db.session.commit()

        request_id = request.form.get('request_id')
        print(request_id)
        if request_id:
            request_to_accept = db.session.query(Request).filter_by(request_id=request_id).first()
            if request_to_accept:
                request_to_accept.status = 'accepted'
                db.session.commit()

        new_post = Post(user_id=employee_id, content=post_content, category=category, points=points)
        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for('feed'))

    else:

        manager_id = session['user_id'] 
        employees = User.query.filter_by(manager_id=manager_id).all()

        user_id = request.args.get('user_id')
        description = request.args.get('description')
        values = request.args.get('values')
        request_id = request.args.get('request_id')
        is_manager_view = request.args.get('is_manager_view')


        employee_choices = [(employee.user_id, f"{employee.name} ({employee.user_id})") for employee in employees]
        return render_template('new_blog.html', title = 'New Post', employee_choices=employee_choices, user_id=user_id, description=description, values=values,
                               is_manager_view=is_manager_view,
                               request_id=request_id)

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


@app.route('/requests',methods=['POST','GET'])
def request_route():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    if request.method=='POST':
        description=request.form['Content']
        values=request.form['value']
        new_task=Request(user_id=session["user_id"],description=description,values=values)
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect(url_for('feed'))
        except Exception as e:
            print(f"Error: {e}")
            return redirect(url_for('feed'))    
    else:
        return render_template('request.html')


@app.route("/manager", methods=["GET"])
def manager():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if not session.get("is_manager", False):
        return redirect(url_for("feed"))

    manager_user_id = session["user_id"]
    requests = (
        db.session.query(Request)
        .join(User, Request.user_id == User.user_id)
        .filter(User.manager_id == manager_user_id)
        .filter(Request.status == 'pending') 
        .order_by(Request.timestamp.desc())
        .options(joinedload(Request.user))
        .all()
    )

    return render_template("manager.html", requests=requests)

@app.route('/requests/<int:request_id>', methods=['DELETE'])
def reject_request(request_id):
    request_to_reject = Request.query.get(request_id)

    if request_to_reject:
        request_to_reject.status = 'rejected'
        db.session.commit()

        print(f"Request {request_id} Rejected")

        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error', 'message': 'Request not found'}), 404
@app.route("/likefunction",methods=['POST'])
def likefunction():
    if 'user_id' not in session:
        return redirect(url_for('login'))
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
    
##from here each part is required and is part of redeem
import random
import string
def get_random_string(length):
     letters = string.ascii_uppercase
     result_str=''.join(random.choice(letters) for i in range(length))
     return result_str
@app.route('/redeem_points', methods=['GET', 'POST'])
def redeem_points():
    employee = session['user_id']
    employee_points = User.query.filter_by(user_id=employee).first()

    if employee_points:
        points = employee_points.curr_points
        user_id=employee_points.user_id

        if request.method == 'POST':
            success_messages = []
            error_messages = []
            redeem_option = request.form.get('redeem_option')
            if redeem_option:
                points_key = f"{redeem_option}_points"
                required_points = int(request.form.get(points_key, 0))
                if employee_points.curr_points >= required_points:
                    employee_points.curr_points -= required_points
                    db.session.commit()                   
                    success_messages.append(f'Redeemed {redeem_option.capitalize()} voucher successfully!, {required_points} points deducted.')
                    voucher_name = f"{redeem_option.capitalize()} Voucher"
                    voucher_worth = required_points//10
                    if required_points==0:
                        return render_template('redeem.html',points=points)                    
                else:
                    error_messages.append(f'Insufficient points to redeem {redeem_option.capitalize()}.')

            if success_messages:
                        s="F"+get_random_string(4)+str(voucher_worth)
                        new_coupon = Coupon(user_id=user_id, coupon_name=voucher_name, coupon_code=s)
                        db.session.add(new_coupon)
                        db.session.commit()
                        return render_template('redeem_success.html', points=employee_points.curr_points, s=s, voucher_name=voucher_name, voucher_worth=voucher_worth)
            elif error_messages:
                        return render_template('redeem_success.html', error_messages=error_messages, points=employee_points.curr_points)
        return render_template('redeem.html', points=points)

@app.route("/coupons")
def coupons():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    employee_id=session['user_id']
    print(employee_id)
    details = Coupon.query.with_entities(Coupon.coupon_name, Coupon.coupon_code, Coupon.expiry_date).filter_by(user_id=employee_id).all()
    return render_template('coupons.html', title = 'coupons', len = len(details), details=details)

@app.route("/Profile", methods=['GET'])
def Profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    userid = session['user_id'] 
    employees = User.query.filter_by(user_id=userid).first()
    employee_id = employees.user_id
    employee_name=employees.name
    manager=employees.manager_id
    if manager: 
        manager_query = User.query.filter_by(user_id=manager).first()
        employee_manager=manager_query.name
    employee_points = employees.points
    employee_curr_points=employees.curr_points
    if manager: 
        return render_template('profile.html', title = 'New Post', id=employee_id, name=employee_name, manager=employee_manager, points=employee_points, curr_points=employee_curr_points)
    else:
        return render_template('profile.html', title = 'New Post', id=employee_id, name=employee_name, points=employee_points, curr_points=employee_curr_points)

if __name__ == '__main__':
    app.run(debug=True)



