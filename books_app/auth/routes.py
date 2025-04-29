from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from books_app.models import Book, Author, Genre, User
from books_app.auth.forms import SignUpForm, LoginForm
from books_app.extensions import db, app

# Import app and db from events_app package so that we can run app
from books_app.extensions import app, db, bcrypt

auth = Blueprint("auth", __name__)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        # Create a new user
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            username=form.username.data,
            password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        flash('Account Created.')
        return redirect(url_for('auth.login'))
    return render_template('signup.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.homepage'))
        else:
            flash('Login unsuccessful. Please check username and password.')
    return render_template('login.html', form=form)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.homepage'))

@auth.route('/create_author', methods=['GET', 'POST'])
@login_required
def create_author():
    if request.method == 'POST':
        name = request.form.get('name')
        if not name:
            flash('Author name is required.', 'error')
            return redirect(url_for('auth.create_author'))
        new_author = Author(name=name)
        db.session.add(new_author)
        db.session.commit()
        flash(f'Author {name} created successfully.')
        return redirect(url_for('main.homepage'))
    return render_template('create_author.html')

@auth.route('/create_genre', methods=['GET', 'POST'])
@login_required
def create_genre():
    if request.method == 'POST':
        name = request.form.get('name')
        if not name:
            flash('Genre name is required.', 'error')
            return redirect(url_for('auth.create_genre'))
        new_genre = Genre(name=name)
        db.session.add(new_genre)
        db.session.commit()
        flash(f'Genre {name} created successfully.')
        return redirect(url_for('main.homepage'))
    return render_template('create_genre.html')

@auth.route('/create_book', methods=['GET', 'POST'])
@login_required
def create_book():
    if request.method == 'POST':
        title = request.form.get('title')
        author_id = request.form.get('author_id')
        genre_id = request.form.get('genre_id')

        if not title or not author_id or not genre_id:
            flash('Title, author, and genre are required.', 'error')
            return redirect(url_for('auth.create_book'))
        
        new_book = Book(title=title, author_id=author_id, genre_id=genre_id)
        db.session.add(new_book)
        db.session.commit()
        flash(f'Book {title} created successfully.')
        return redirect(url_for('main.homepage'))
    authors = Author.query.all()
    genres = Genre.query.all()
    return render_template('create_book.html', authors=authors, genres=genres)

@auth.route('/favorite_books/<book_id>', methods=['POST'])
@login_required
def favorite_book(book_id):
    book = Book.query.get(book_id)
    if book not in current_user.favorite_books:
        current_user.favorite_books.append(book)
        db.session.commit()
        flash(f"Added {book.title} to favorites.")
    return redirect(url_for('main.book_detail', book_id=book_id))

@auth.route('/unfavorite_books/<book_id>', methods=['POST'])
@login_required
def unfavorite_book(book_id):
    book = Book.query.get(book_id)
    if book in current_user.favorite_books:
        current_user.favorite_books.remove(book)
        db.session.commit()
        flash(f"Removed {book.title} from favorites.")
    return redirect(url_for('main.book_detail', book_id=book_id))