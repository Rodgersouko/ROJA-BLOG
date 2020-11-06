from flask import Flask, render_template, url_for, flash, redirect, abort, request
from . import main
from .forms import RegistrationForm, LoginForm, BlogForm, UpdateProfile, CommentForm
from app.requests import get_quotes
from ..models import User, Blog, Comment
from .. import db, photos
from flask_login import login_user,login_required, logout_user, current_user

@main.route('/')
def home():
    quotes = get_quotes()
    page = request.args.get('page',1, type = int )
    return render_template('index.html', quote = quotes)

@main.route('/display_blog')
@login_required
def display_blog():
    blogs = Blog.query.order_by(Blog.posted.desc())
    return render_template('display_blogs.html',blogs=blogs)

@main.route('/signout')
@login_required
def signout():
    logout_user()
    return redirect(url_for("main.home"))

@main.route('/register', methods = ['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username = form.username.data,email = form.email.data,password = form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for { form.username.data }!','success')
        return redirect(url_for('.home'))
    return render_template('register.html', title = 'register', form = form)

@main.route('/login' , methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user,form.remember.data)
            flash('You have been logged in successfully!', 'success')
            return redirect(url_for('.home'))
    else:
        flash('login unsuccessful. Please check your password or email', 'danger')

    return render_template('login.html', title = 'login', form = form)

@main.route('/new_post', methods=['POST','GET'])
@login_required
def blog():
    form = BlogForm()
    if form.validate_on_submit():
        title = form.title.data
        blog_content = form.blog_content.data
        user_id =  current_user._get_current_object().id
        blog = Blog(title=title,blog_content=blog_content,user_id=user_id)
        blog.save()
        return redirect(url_for('.display_blog'))
    return render_template('blog.html', form = form)

@main.route('/user/<uname>')
def profile(uname):
    user = User.query.filter_by(username = uname).first()

    if user is None:
        abort(404)

    return render_template("profile/profile.html", user = user)

@main.route('/user/<uname>/update',methods = ['GET','POST'])
@login_required
def update_profile(uname):
    user = User.query.filter_by(username = uname).first()
    if user is None:
        abort(404)

    form = UpdateProfile()

    if form.validate_on_submit():
        user.bio = form.bio.data

        db.session.add(user)
        db.session.commit()

        return redirect(url_for('.profile',uname=user.username))

    return render_template('profile/update.html',form =form)

@main.route('/user/<uname>/update/pic',methods= ['POST'])
@login_required
def update_pic(uname):
    user = User.query.filter_by(username = uname).first()
    if 'photo' in request.files:
        filename = photos.save(request.files['photo'])
        path = f'photos/{filename}'
        user.profile_pic_path = path
        db.session.commit()
    return redirect(url_for('main.profile',uname=uname))

@main.route('/comment/<int:blog_id>', methods = ['POST','GET'])
@login_required
def comment(blog_id):
    form = CommentForm()
    comment = Comment.query.get(blog_id)
    users_comments = Comment.query.filter_by(blog_id = blog_id).all()
    if form.validate_on_submit():
        comment = form.comment.data 
        blog_id = blog_id
        user_id = current_user._get_current_object().id
        new_comment = Comment(comment = comment,user_id = user_id,blog_id = blog_id)
        new_comment.save_comment()
        return redirect(url_for('.comment', blog_id = blog_id))
    return render_template('comment.html', form =form, comment = comment,users_comments=users_comments)

@main.route('/blog/<blog_id>/delete', methods = ['POST','GET'])
@login_required
def delete_blog(blog_id):
    blog = Blog.query.get(blog_id)
    Blog.delete(blog)
    return redirect(url_for('main.home'))

@main.route('/comment/<comment_id>/delete', methods = ['POST','GET'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get(comment_id)
    Comment.delete(comment)
    return redirect(url_for('main.home'))