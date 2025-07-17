from flask import render_template, request
from app import app
from datetime import datetime


# Задание 2 Lesson 9(Flask)
# Список участников команды
team_members = [
    {'name': 'Анна', 'role': 'Главный разработчик'},
    {'name': 'Иван', 'role': 'UX/UI дизайнер'},
    {'name': 'Мария', 'role': 'Менеджер проектов'},
    {'name': 'Дмитрий', 'role': 'Тестировщик'},
    {'name': 'Ольга', 'role': 'Бизнес-аналитик'}
]


@app.route("/")
def home():
    current_datetime = datetime.now()
    return render_template("index.html", current_datetime=current_datetime)


@app.route('/about')
def about():

    # Передаем в шаблон
    return render_template('about.html', team_members=team_members)


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Получаем данные из формы
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        # Перенаправляем с сообщением об успехе
        return render_template('contact.html',
                               success=True,
                               name=name,
                               email=email,
                               message=message,
                               success_message="Thank you! Your message has been sent successfully!")

    return render_template('contact.html')
