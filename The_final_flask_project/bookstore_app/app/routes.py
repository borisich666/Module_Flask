from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import random
from app import db
from app.models import User, Book, Order, OrderItem, Review
from app.forms import RegistrationForm, LoginForm, ReviewForm, CheckoutForm, ConfirmCodeForm

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    top_books = Book.query.order_by(Book.rating.desc()).limit(3).all()
    genres = db.session.query(Book.genre).distinct().all()
    genres = [genre[0] for genre in genres]
    return render_template('index.html', top_books=top_books, genres=genres)


@bp.route('/catalog')
@bp.route('/catalog/<genre>')
def catalog(genre=None):
    page = request.args.get('page', 1, type=int)
    per_page = 12

    if genre:
        books = Book.query.filter_by(genre=genre).paginate(page=page, per_page=per_page)
    else:
        books = Book.query.paginate(page=page, per_page=per_page)

    genres = db.session.query(Book.genre).distinct().all()
    genres = [genre[0] for genre in genres]

    return render_template('catalog.html', books=books, genres=genres, current_genre=genre)


@bp.route('/book/<int:book_id>', methods=['GET', 'POST'])
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    form = ReviewForm()
    reviews = Review.query.filter_by(book_id=book_id).order_by(Review.created_at.desc()).all()

    if form.validate_on_submit() and current_user.is_authenticated:
        review = Review(
            user_id=current_user.id,
            book_id=book_id,
            rating=form.rating.data,
            comment=form.comment.data
        )
        db.session.add(review)
        db.session.commit()
        flash('Отзыв успешно добавлен!', 'success')
        return redirect(url_for('main.book_detail', book_id=book_id))

    return render_template('book_detail.html', book=book, form=form, reviews=reviews)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        # Проверяем, существует ли пользователь
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Пользователь с таким email уже существует', 'error')
            return redirect(url_for('main.register'))

        # Создаем пользователя
        user = User(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            password=generate_password_hash(form.password.data),
            confirmation_code=str(random.randint(100000, 999999))
        )
        db.session.add(user)
        db.session.commit()

        # Имитация отправки кода
        flash(f'Код подтверждения: {user.confirmation_code} (в реальном приложении отправлен по SMS)', 'info')
        session['pending_user_id'] = user.id
        return redirect(url_for('main.confirm_code'))

    return render_template('register.html', form=form)


@bp.route('/confirm-code', methods=['GET', 'POST'])
def confirm_code():
    if 'pending_user_id' not in session:
        return redirect(url_for('main.register'))

    form = ConfirmCodeForm()
    user = User.query.get(session['pending_user_id'])

    if form.validate_on_submit():
        if form.code.data == user.confirmation_code:
            user.is_confirmed = True
            db.session.commit()
            session.pop('pending_user_id')
            flash('Регистрация завершена успешно! Теперь вы можете войти.', 'success')
            return redirect(url_for('main.login'))
        else:
            flash('Неверный код подтверждения', 'error')

    return render_template('confirm_code.html', form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and check_password_hash(user.password, form.password.data):
            if user.is_confirmed:
                login_user(user)
                next_page = request.args.get('next')
                flash('Вы успешно вошли в систему!', 'success')
                return redirect(next_page or url_for('main.index'))
            else:
                flash('Аккаунт не подтвержден. Пожалуйста, подтвердите email.', 'error')
        else:
            flash('Неверный email или пароль', 'error')

    return render_template('login.html', form=form)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('main.index'))


@bp.route('/add-to-cart/<int:book_id>')
@login_required
def add_to_cart(book_id):
    if 'cart' not in session:
        session['cart'] = []

    cart = session['cart']

    # Ищем книгу в корзине
    book_found = False
    for item in cart:
        if item['book_id'] == book_id:
            item['quantity'] += 1
            book_found = True
            break

    if not book_found:
        book = Book.query.get(book_id)
        if book:
            cart.append({
                'book_id': book_id,
                'title': book.title,
                'author': book.author,
                'price': float(book.price),
                'cover_url': book.cover_url,
                'quantity': 1
            })

    session['cart'] = cart
    flash('Книга добавлена в корзину', 'success')
    return redirect(url_for('main.cart'))


@bp.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)


@bp.route('/remove-from-cart/<int:item_index>')
def remove_from_cart(item_index):
    cart = session.get('cart', [])

    # Преобразуем индекс в int и проверяем границы
    try:
        index = int(item_index)
        if 0 <= index < len(cart):
            removed_item = cart.pop(index)
            session['cart'] = cart
            flash(f'"{removed_item["title"]}" удалена из корзины', 'info')
        else:
            flash('Неверный индекс элемента', 'error')
    except (ValueError, TypeError):
        flash('Неверный индекс элемента', 'error')

    return redirect(url_for('main.cart'))


@bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    form = CheckoutForm()
    cart_items = session.get('cart', [])

    if not cart_items:
        flash('Ваша корзина пуста', 'warning')
        return redirect(url_for('main.cart'))

    if form.validate_on_submit():
        total = sum(item['price'] * item['quantity'] for item in cart_items)

        order = Order(
            user_id=current_user.id,
            delivery_method=form.delivery_method.data,
            delivery_address=form.address.data if form.delivery_method.data == 'delivery' else None,
            total_amount=total
        )
        db.session.add(order)
        db.session.commit()

        for item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                book_id=item['book_id'],
                quantity=item['quantity'],
                price=item['price']
            )
            db.session.add(order_item)

        db.session.commit()
        session['cart'] = []

        flash('Заказ успешно оформлен! Номер заказа: #{}'.format(order.id), 'success')
        return redirect(url_for('main.orders'))

    return render_template('checkout.html', form=form, cart_items=cart_items)


@bp.route('/orders')
@login_required
def orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.order_date.desc()).all()
    return render_template('orders.html', orders=orders)


@bp.route('/search')
def search():
    query = request.args.get('q', '')
    if query:
        books = Book.query.filter(
            (Book.title.ilike(f'%{query}%')) |
            (Book.author.ilike(f'%{query}%')) |
            (Book.genre.ilike(f'%{query}%'))
        ).all()
    else:
        books = []

    return render_template('search.html', books=books, query=query)