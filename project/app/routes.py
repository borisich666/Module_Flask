from flask import render_template, request
from app import app


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


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
