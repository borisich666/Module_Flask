from flask import Flask


# Создаем объект приложения Flask
app = Flask(__name__)




# Задание 1 Lesson 9(Flask)
# Создаем фильтр для форматирования даты
@app.template_filter('russian_date')
def format_russian_date(dt):
    return dt.strftime('%A, %B %d, %Y, %H:%M:%S')


# Запуск приложения
if __name__ == "__main__":
    app.run(debug=True)