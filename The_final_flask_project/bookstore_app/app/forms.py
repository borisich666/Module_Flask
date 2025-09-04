from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional


class RegistrationForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Телефон', validators=[DataRequired(), Length(min=10, max=15)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Зарегистрироваться')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class ReviewForm(FlaskForm):
    rating = SelectField('Оценка',
                        choices=[(5, '5 - Отлично'), (4, '4 - Хорошо'),
                                (3, '3 - Удовлетворительно'), (2, '2 - Плохо'),
                                (1, '1 - Ужасно')],
                        coerce=int,
                        validators=[DataRequired()])
    comment = TextAreaField('Комментарий', validators=[Length(max=500), Optional()])
    submit = SubmitField('Оставить отзыв')


class CheckoutForm(FlaskForm):
    delivery_method = SelectField('Способ доставки',
                                 choices=[('pickup', 'Самовывоз'),
                                         ('delivery', 'Доставка до двери')],
                                 validators=[DataRequired()])
    address = TextAreaField('Адрес доставки', validators=[Optional()])
    submit = SubmitField('Оформить заказ')


class ConfirmCodeForm(FlaskForm):
    code = StringField('Код подтверждения', validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Подтвердить')