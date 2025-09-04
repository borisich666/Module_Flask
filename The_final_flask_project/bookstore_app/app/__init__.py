from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

# Инициализация расширений
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице.'


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Инициализация расширений с приложением
    db.init_app(app)
    login_manager.init_app(app)

    # Настройка user_loader
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Импорт и регистрация маршрутов
    from app.routes import bp
    app.register_blueprint(bp)

    return app