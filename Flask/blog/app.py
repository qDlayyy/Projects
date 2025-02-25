import bcrypt
from flask import Flask, render_template, request, redirect, session, flash, url_for
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError
from datetime import timedelta

from config import Config
from key import APP_SECRET_KEY
from models import db, Users, Posts, Comments, Ratings
from service import get_comment_data, get_post_data, get_post_rating, get_author


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
app.secret_key = APP_SECRET_KEY
app.permanent_session_lifetime = timedelta(hours=1)


def setup():
    inspector = inspect(db.engine)

    if not inspector.has_table('users'):
        db.create_all()
        print('ddd')
    
    anonymous_user = Users.query.filter_by(username="Anonymous").first()
    
    if not anonymous_user:
        password = '123123123'
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        anonymous_user = Users(username="Anonymous", password_hash=hashed_password, email='123@gmail.com')
        db.session.add(anonymous_user)
        db.session.commit()
    
    else:
        pass


def login_required(func):
    def wrapper(*args, **kwargs):
        if session.get('user_id', None) == None:

            return redirect(url_for('login'))
        
        return func(*args, **kwargs)
    
    return wrapper


@app.context_processor
def inject_user():

    return dict(user_id=session.get('user_id'))


@app.route('/')
def home():
    username = session.get('username', None)

    return render_template('index.html', username=username)


@login_required
@app.route('/create/', methods=['GET', 'POST'])
def post_create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        user_id = session['user_id']
        post = Posts(title=title, content=content, author=user_id)
        
        try:
            db.session.add(post)
            db.session.commit()
            return redirect(url_for('posts'))
        
        except Exception as e:
            db.session.rollback()
            return f'Exception has been raised: {e}.'
        
    else:
        return render_template('post_creation.html')
    

@app.route('/posts/')
def posts():
    posts = Posts.query.order_by(Posts.id.desc()).all()

    return render_template('posts.html', posts=posts)


@app.route('/posts/<int:post_id>', methods=['GET', 'POST'])
def post(post_id):
    if request.method == 'POST':
        user_id = session.get('user_id', None)
        
        if user_id:
            content = request.form['content']
            reply_to = session.get('reply_to')
            
            try:
                comment = Comments(post=post_id, content=content, author=user_id, parent_id=reply_to)
                db.session.add(comment)
                db.session.commit()
                session['reply_to'] = None

            except Exception as e:
                flash(f'Some exceptions have been raised. {e}.', category='error')
                db.session.rollback()
            
            return redirect(url_for('post', post_id=post_id))

        else:
            return redirect(url_for('login'))

    else:
        post = Posts.query.filter_by(id=post_id).first()

        if not post:
            return redirect(url_for('home'))
        
        author = Users.query.filter_by(id=post.author).first()
        comments = Comments.query.filter_by(post=post.id).order_by(Comments.id.desc()).all()
    
        post_data = get_post_data(post)

        comments_data_list = []
        if comments:
            for comment in comments:
                comment_data = get_comment_data(comment)
                comments_data_list.append(comment_data) 


        if not post or not author:
            flash('Post not found.', category='error')
            return redirect(url_for('home'))
        
        reply_comment_id = session.get('reply_to')
        reply_comment_author = None 
        
        if reply_comment_id:
            reply_comment = Comments.query.filter_by(id=reply_comment_id).first()
            reply_comment_author = Users.query.filter_by(id=reply_comment.author).first().username

        star_list = get_post_rating(post)
        
        is_deletable = True if post.author == session.get('user_id') else False

        return render_template('post.html',post_id=post_id, post=post_data, comments=comments_data_list, reply_comment_author=reply_comment_author, star_list=star_list,  is_deletable=is_deletable)
    

@login_required
@app.route('/destroy/<int:post_id>/')
def destroy(post_id):
    post = Posts.query.filter_by(id=post_id).first()

    if post:
        user_id = session.get('user_id')
        
        if post.author == user_id:
            try:
                Comments.query.filter_by(post=post_id).delete()

                db.session.delete(post)
                db.session.commit()

                return redirect('home')

            except Exception as e:
                db.session.rollback()
                flash(f'Error has occured. {e}.', category='error')

        else:
            flash('You cannot delete this post.', category='error')

    else:
        flash('There is no such post.', category='warning')
        return redirect(url_for('posts'))


@login_required
@app.route('/reply_to/<int:comment_id>/<int:post_id>/')
def reply(comment_id, post_id):
    if comment_id == 0:
        session['reply_to'] = None
        print(session['reply_to'])
    
    else:
        session['reply_to'] = comment_id
    
    return redirect(url_for('post', post_id=post_id))


@app.route('/registration/', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        try:
            user_exists = Users.query.filter_by(username=username).first()
            
            if user_exists:
                raise IntegrityError()
            
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            user = Users(username=username, email=email, password_hash=hashed_password)
            db.session.add(user)
            db.session.commit()
        
        except IntegrityError:
            flash('Such user has already been registered.', category='error')
        
        except Exception as e:
            flash(f'Some other errors has been rased. {e}.', category='error')
    
        return redirect(url_for('login'))
    
    return render_template('registration.html')


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            print(hashed_password)
            user = Users.query.filter_by(username=username).first() 
            
            if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash):
                session['user_id'] = user.id
                session['username'] = username
                flash('You are now logged in!', category='success')
                return redirect(url_for('home'))

            else:
                print('ff')
                flash('There is no user with that username and password', category='danger')
        
        except Exception as e:
            flash(f'Some other errors has been rased. {e}.', category='error')

    return render_template('login.html')


@app.route('/logout/')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    
    return redirect(url_for('home'))


@login_required
@app.route('/rate/<int:post_id>/<int:value>/')
def rate(post_id, value):
    user_id = session.get('user_id')
    
    if user_id:
        current_rating = Ratings.query.filter_by(user=user_id).first()
        try:
            if current_rating:
                current_rating.rating = value
                db.session.add(current_rating)
                db.session.commit()
            
            else:
                rate = Ratings(user=session.get('user_id'), post=post_id, rating=value)

                db.session.add(rate)
                db.session.commit()
        
        except Exception as e:
            db.session.rollback()
            flash(f'An Error has occured. {e}.', category='error')
        
        return redirect(url_for('post', post_id=post_id))

    else:
        print('fff')
        return redirect(url_for('login'))


if __name__ == "__main__":
    with app.app_context():
        setup()
    app.run(debug=True)