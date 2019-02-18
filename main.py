from flask import Flask, request, redirect, render_template, session, flash, url_for
from datetime import datetime
import re
import cgi
from app import app, db
from models import User, Blog
from hashutils import make_pw_hash, check_pw_hash

def isvalidpost(title,newpost):
    title_error = ''
    blog_error = ''
    if not title:
        title_error = 'Please fill in the title'
    if not newpost:
        blog_error = 'Please fill in the body'
    return (title_error, blog_error)

def isvalidusername(username):
    if len(username) < 4:
        return 'Please select a username with at least 4 characters.'
    if not re.fullmatch(r'[0-9a-zA-Z]+', username):
        return 'Please use only letter and numbers in the username.'
    return # return NULL if valid username

def isvalidpassword(password, verify):
    if len(password) < 4:
        return 'Please select a password with at least 4 characters.'
    if not re.fullmatch(r'[0-9a-zA-Z]+', password):
        return 'Please use only letters and numbers in the password.'
    if not password == verify:
        return 'Passwords do not match.'
    return # return NULL if valid username

def get_current_user():
    return get_user(session['username'])

def get_user(username):
    return (User.query.filter_by(username=username).first())

allowed_routes = ['signup', 'login', 'index', 'blog', 'preferences']

@app.before_request
def require_login():
    if not ('username' in session or request.endpoint in allowed_routes):
        return redirect("/")

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    del session['username']
    flash('Logged out.')
    return redirect('/blog')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user:
            if check_pw_hash(password, user.pw_hash):
                session['username'] = username
                flash('Welcome {}!'.format(username))
                return redirect('/')
        flash('Password incorrect or user does not exist', 'err')
    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']    
        username_error = isvalidusername(username)
        password_error = isvalidpassword(password, verify)
        user = get_user(username)
        if user:
            username_error = 'Username "' + username + '" already exists.'
        if not (username_error or password_error):
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/')
        else:
            if username_error:
                flash(username_error, 'err')
            if password_error:
                flash(password_error, 'err')
    return render_template('signup.html')

@app.route('/preferences', methods=['POST'])
def preferences():
    session['blogz-per-page'] = request.form['blogz-per-page']
    user = request.args.get('user', 'all')
    flash('Blogs per page set to {}.'.format(session['blogz-per-page']))
    return redirect('/blog?user={}'.format(user))

@app.route('/newpost', methods=['POST', 'GET'])        
def newpost():
    error = request.args.get("error")
    if request.method == 'POST':
        title = request.form['title']
        newpost = request.form['newpost']
        title_error, blog_error = isvalidpost(title,newpost)
        if (title_error or blog_error):
            return render_template('newpost.html', page_title='Add a Blog Entry', title_error=title_error, blog_error=blog_error, title=title, newpost=newpost)
        owner = get_current_user()
        new_blog_post = Blog(title, newpost, owner)
        db.session.add(new_blog_post)
        db.session.commit()
        return redirect('/blog?id={}'.format(new_blog_post.id))
    return render_template('newpost.html', page_title='Add a Blog Entry', error=error)

@app.route("/blog")
def blog():
    if not 'blogz-per-page' in session:
        session['blogz-per-page'] = '10'
    try:
        per_page = int(session['blogz-per-page'])
    except:
        per_page = None
    page = int(request.args.get('page',1))
    id = request.args.get('id')
    if id:
        id = int(id)
        the_blogs = Blog.query.filter_by(id=id).first()
        if the_blogs:
            title=the_blogs.title
            return render_template('1blog.html', page_title=title, post=the_blogs)
        flash('No post found with id = {}.'.format(id), 'err')
        return render_template('blog.html', page_title='Build a Blog')        
    user = request.args.get('user')
    if user and user != 'all':
        owner = get_user(user)
        if owner:
            page = int(request.args.get('page',1))
            the_blogs = Blog.query.filter_by(owner_id=owner.id).order_by('post_datetime DESC').paginate(page,per_page,error_out=False)
            return render_template('blog.html', page_title='Blogs for {}'.format(user), posts=the_blogs, user=user)
        flash('User {} not found.'.format(user), 'err')
        return render_template('blog.html', page_title='Build a Blog')        
    the_blogs = Blog.query.order_by('post_datetime DESC').paginate(page,per_page,error_out=False)
    return render_template('blog.html', page_title='Build a Blog', posts=the_blogs, user='all')

@app.route("/")
def index():
    users = User.query.all()
    return render_template('index.html', users=users)
    return redirect('/blog')

if __name__ == "__main__":
    app.run()
