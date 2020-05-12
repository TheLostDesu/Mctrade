from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm
from app.forms import CreateSellForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post, Item, Request
from werkzeug.urls import url_parse
from datetime import datetime


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    try:
        db.create_all()
    except Exception:
        print("Ok")
    if not current_user.is_authenticated:
        user = {'username': "Анон"}
        posts = Post.query.order_by(Post.timestamp.desc()).all()
        return render_template("index2.html", title='Home Page', user=user,
                               posts=posts)
    else:
        form = PostForm()
        if form.validate_on_submit():
            post = Post(body=form.post.data, author=current_user)
            db.session.add(post)
            db.session.commit()
            flash('Your post is now live!')
            return redirect('/index')
        posts = Post.query.order_by(Post.timestamp.desc()).all()
        return render_template("index.html", title='Home Page', form=form,
                               posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        db.create_all()
    except Exception:
        print("Ok")
    if current_user.is_authenticated:
        return redirect('/index')
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(username=form.username.data).first()
            if user is None or not user.check_password(form.password.data):
                flash('Invalid username or password')
                return redirect(url_for('login'))
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = '/index'
            return redirect('/index')
        except Exception:
            db.create_all()
            print(1)
            user = User.query.filter_by(username=form.username.data).first()
            if user is None or not user.check_password(form.password.data):
                flash('Invalid username or password')
                return redirect(url_for('login'))
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = '/index'
            return redirect('/index')
    return render_template('login.html', title='Sign In', form=form)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/index')


@app.route('/register', methods=['GET', 'POST'])
def register():
    try:
        db.create_all()
    except Exception:
        print('db was created YET')

    if current_user.is_authenticated:
        return redirect('/index')
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('login'))
        except Exception:
            db.create_all()
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)


@app.route('/sell', methods=['GET', 'POST'])
@login_required
def sell():
    form = CreateSellForm()
    if form.validate_on_submit():
        if not form.itemcount.data.isdigit():
            flash('Please input correct count data')
            return redirect(url_for('sell'))
        if not form.itemcost.data.isdigit():
            flash('Please input correct cost  data')
            return redirect(url_for('sell'))
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = '/index'

        itemname = form.itemname.data.lower()
        count = int(form.itemcount.data)
        cost = int(form.itemcost.data)
        seller = current_user.id

        itemid = Item.query.filter_by(name=itemname).first()
        if itemid is None:
            itm = Item(name=itemname)
            db.session.add(itm)
            db.session.commit()

        itemid = Item.query.filter_by(name=itemname).first().id
        trade = Request(user_id=seller, item_id=itemid, count=count, cost=cost)
        db.session.add(trade)
        db.session.commit()
        flash('Request get')
        return redirect('/index')
    return render_template('cratesellreq.html', title='Create new sell rq',
                           form=form)


@app.route('/buy')
def buy_all():
    posts = Item.query.order_by(Item.name).all()
    return render_template('rqbuy.html', title='Buy something', posts=posts)


@app.route('/buy/<itemid>')
def buy(itemid):
    post = Request.query.filter_by(item_id=int(itemid))
    return render_template('buyitem.html', title='Buy item', posts=post)


@app.route('/buyitem/<tradeid>')
def buy2(traded):
    return 'ok'
