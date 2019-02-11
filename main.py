from flask import Flask, request, redirect, render_template, session
from datetime import datetime
import re
import cgi
from app import app, db
from models import User, Blog

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
    if not re.fullmatch(r'\w+', username):
        return 'Please use only A-Z, 0-9 and underscore in the username.'
    return # return NULL if valid username

def isvalidpassword(password, verify):
    if len(password) < 4:
        return 'Please select a password with at least 4 characters.'
    if not re.fullmatch(r'\w+', password):
        return 'Please use only A-Z, 0-9 and underscore in the password.'
    if not password == verify:
        return 'Passwords do not match.'
    return # return NULL if valid username

def get_owner(username):
    return (User.query.filter_by(username=username).first())

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']    
        username_error = isvalidusername(username)
        password_error = isvalidpassword(password, verify)
        user = get_owner(username)
        if user:
            username_error = 'Username: ' + username + 'already exists.'
        if not (username_error or password_error):
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/')
        else:
            # TODO user already exists
            return (str(username_error) +  '<br />' + str(password_error))
        
    return render_template('signup.html')


@app.route('/newpost', methods=['POST', 'GET'])        
def newpost():
    error = request.args.get("error")
    if request.method == 'POST':
        title = request.form['title']
        newpost = request.form['newpost']
        title_error, blog_error = isvalidpost(title,newpost)
        if (title_error or blog_error):
            return render_template('newpost.html', page_title='Add a Blog Entry', title_error=title_error, blog_error=blog_error, title=title, newpost=newpost)
        new_blog_post = Blog(title, newpost)
        db.session.add(new_blog_post)
        db.session.commit()
        return redirect('/blog?id={}'.format(new_blog_post.id))
    return render_template('newpost.html', page_title='Add a Blog Entry', error=error)

@app.route("/blog")
def blog():
    id = request.args.get("id")
    if id:
        the_blogs = Blog.query.filter_by(id=id).first()
        if the_blogs:
            title=the_blogs.title
            return render_template('1blog.html', page_title=title, post=the_blogs)
        return redirect('/') # there was no db return with the requested id.
    the_blogs = Blog.query.order_by('post_datetime DESC').all()
    return render_template('blog.html', page_title='Build a Blog', posts=the_blogs)

@app.route("/")
def index():
    return redirect('/blog')

if __name__ == "__main__":
    app.run()
