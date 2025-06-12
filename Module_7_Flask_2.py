from flask import Flask

# Создаем объект приложения Flask
app = Flask(__name__)


# Определяем маршрут и привязываем его к функции
# Задание 1: Простые маршруты
@app.route('/Hello')
def hello():
    return "Hello, Word!"


@app.route('/info')
def info():
    return "This is an informational page."


# Задание 2: Динамические маршруты - сумма чисел
@app.route('/calc/<int:num1>/<int:num2>')
def calc(num1, num2):
    return f"The sum of {num1} and {num2} is {num1 + num2}."


# Задание 3: Переворот текста
@app.route('/reverse/<string:text>')
def reverse_text(text):
    return text[::-1]


# Задание 4: Приветствие с возрастом
@app.route('/user/<string:name>/<int:age>')
def user_info(name, age):
    return f"Hello, {name}. You are {age} years old."


# Запуск приложения
if __name__ == "__main__":
    app.run(debug=True)
