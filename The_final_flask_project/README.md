Описание:

Это учебное веб-приложение интернет-магазина книг, разработанное с использованием Flask.
Пользователи могут просматривать каталог, регистрироваться, добавлять книги в корзину и оформлять заказы.


Запуск проекта:

Установите зависимости:
pip install flask flask-sqlalchemy flask-login flask-wtf

Создайте базу данных: 

python -c " from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print('База данных создана')
"

Импортируйте книги: 
python import_books.py

Запустите приложение:
python run.py