
from flask import render_template, url_for, flash, redirect, request, session
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm
from app.models import User, Post
from flask_login import login_required, login_user, logout_user, current_user

@app.route('/')
@app.route('/home')
@login_required
def home():
    return render_template('home.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Аккаунт создан. Пожалуйста, авторизуйтесь!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash("Вы успешно вошли в систему!", "success")
            return redirect(url_for('home'))
        else:
            flash("Неверный логин или пароль. Попробуйте снова.", "danger")
    return render_template("login.html", title="Login", form=form)


@app.route("/logout")
def logout():
    logout_user()
    session.pop('_flashes', None)
    flash('Вы вышли из аккаунта', 'info')
    return redirect(url_for('login'))


@app.route("/posts")
@login_required
def posts():
    all_posts = Post.query.all()
    return render_template('posts.html', posts=all_posts)


@app.route("/create_post", methods=['POST', 'GET'])
@login_required
def create_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        post = Post(title=title, content=content, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        flash('Статья успешно опубликована!', 'success')
        return redirect(url_for('posts'))
    return render_template('create_post.html')


@app.route("/post/<int:post_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.id:
        return redirect(url_for('posts'))

    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        db.session.commit()
        flash('Статья успешно обновлена!', 'success')
        return redirect(url_for('posts'))

    return render_template('edit_post.html', post=post)


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.id:
        return redirect(url_for('posts'))

    db.session.delete(post)
    db.session.commit()
    flash('Статья удалена', 'danger')
    return redirect(url_for('posts'))
