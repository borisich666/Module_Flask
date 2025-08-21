from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import random

app = Flask(__name__)
app.secret_key = 'supersecretkey'


# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('agents.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS agents
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  codename TEXT NOT NULL,
                  phone TEXT,
                  email TEXT NOT NULL,
                  access_level TEXT NOT NULL,
                  notes TEXT)''')
    conn.commit()
    conn.close()


# Генератор кодовых имен
def generate_codename():
    adjectives = ['Shadow', 'Steel', 'Midnight', 'Silent', 'Phantom', 'Iron', 'Black', 'Red', 'Golden', 'Lone']
    nouns = ['Wolf', 'Fox', 'Eagle', 'Bear', 'Raven', 'Hawk', 'Falcon', 'Panther', 'Ghost', 'Spy']
    return f"{random.choice(adjectives)} {random.choice(nouns)}"


# Главная страница - список всех агентов
@app.route('/')
def index():
    conn = sqlite3.connect('agents.db')
    c = conn.cursor()
    c.execute("SELECT * FROM agents")
    agents = c.fetchall()
    conn.close()

    dark_mode = request.cookies.get('dark_mode', 'false')
    return render_template('index.html', agents=agents, dark_mode=dark_mode)


# Добавление нового агента
@app.route('/add', methods=['GET', 'POST'])
def add_agent():
    if request.method == 'POST':
        codename = request.form.get('codename', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        access_level = request.form.get('access_level', '').strip()
        notes = request.form.get('notes', '').strip()

        # Если кодовое имя не указано, генерируем автоматически
        if not codename:
            codename = generate_codename()

        # Проверка обязательных полей
        if not email or not access_level:
            flash('Заполните обязательные поля: Email и Уровень доступа!', 'danger')
            return render_template('add_agent.html',
                                   codename=codename,
                                   phone=phone,
                                   email=email,
                                   access_level=access_level,
                                   notes=notes,
                                   dark_mode=request.cookies.get('dark_mode', 'false'))

        try:
            conn = sqlite3.connect('agents.db')
            c = conn.cursor()
            c.execute("INSERT INTO agents (codename, phone, email, access_level, notes) VALUES (?, ?, ?, ?, ?)",
                      (codename, phone, email, access_level, notes))
            conn.commit()
            conn.close()

            flash(f'Агент "{codename}" успешно добавлен!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Ошибка при добавлении агента: {str(e)}', 'danger')
            return render_template('add_agent.html',
                                   codename=codename,
                                   phone=phone,
                                   email=email,
                                   access_level=access_level,
                                   notes=notes,
                                   dark_mode=request.cookies.get('dark_mode', 'false'))

    dark_mode = request.cookies.get('dark_mode', 'false')
    return render_template('add_agent.html',
                           codename=generate_codename(),
                           dark_mode=dark_mode)


# Просмотр досье агента
@app.route('/agent/<int:agent_id>')
def view_agent(agent_id):
    conn = sqlite3.connect('agents.db')
    c = conn.cursor()
    c.execute("SELECT * FROM agents WHERE id=?", (agent_id,))
    agent = c.fetchone()
    conn.close()

    if not agent:
        flash('Агент не найден!', 'danger')
        return redirect(url_for('index'))

    dark_mode = request.cookies.get('dark_mode', 'false')
    return render_template('view_agent.html', agent=agent, agent_id=agent_id, dark_mode=dark_mode)


# Редактирование агента
@app.route('/edit/<int:agent_id>', methods=['GET', 'POST'])
def edit_agent(agent_id):
    conn = sqlite3.connect('agents.db')
    c = conn.cursor()

    if request.method == 'POST':
        codename = request.form.get('codename', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        access_level = request.form.get('access_level', '').strip()
        notes = request.form.get('notes', '').strip()

        if not codename or not email or not access_level:
            flash('Заполните обязательные поля!', 'danger')
            return redirect(url_for('edit_agent', agent_id=agent_id))

        try:
            c.execute("UPDATE agents SET codename=?, phone=?, email=?, access_level=?, notes=? WHERE id=?",
                      (codename, phone, email, access_level, notes, agent_id))
            conn.commit()
            flash('Данные агента обновлены!', 'success')
        except Exception as e:
            flash(f'Ошибка при обновлении: {str(e)}', 'danger')
        finally:
            conn.close()

        return redirect(url_for('view_agent', agent_id=agent_id))

    # GET запрос - показать форму редактирования
    c.execute("SELECT * FROM agents WHERE id=?", (agent_id,))
    agent = c.fetchone()
    conn.close()

    if not agent:
        flash('Агент не найден!', 'danger')
        return redirect(url_for('index'))

    dark_mode = request.cookies.get('dark_mode', 'false')
    return render_template('edit_agent.html', agent=agent, agent_id=agent_id, dark_mode=dark_mode)


# Удаление агента
@app.route('/delete/<int:agent_id>', methods=['POST'])
def delete_agent(agent_id):
    conn = sqlite3.connect('agents.db')
    c = conn.cursor()
    c.execute("DELETE FROM agents WHERE id=?", (agent_id,))
    conn.commit()
    conn.close()

    flash('Досье агента уничтожено!', 'warning')
    return redirect(url_for('index'))


# Поиск агентов
@app.route('/search', methods=['GET', 'POST'])
def search_agents():
    agents = []
    search_term = ''
    selected_access_level = ''

    if request.method == 'POST':
        search_term = request.form.get('search_term', '').strip()
        selected_access_level = request.form.get('access_level', '').strip()

        conn = sqlite3.connect('agents.db')
        c = conn.cursor()

        try:
            if selected_access_level:
                # Поиск по кодовому имени и уровню доступа
                c.execute("SELECT * FROM agents WHERE codename LIKE ? AND access_level = ?",
                          (f"%{search_term}%", selected_access_level))
            else:
                # Поиск только по кодовому имени
                c.execute("SELECT * FROM agents WHERE codename LIKE ?",
                          (f"%{search_term}%",))

            agents = c.fetchall()
        except Exception as e:
            flash(f'Ошибка при поиске: {str(e)}', 'danger')
        finally:
            conn.close()

    dark_mode = request.cookies.get('dark_mode', 'false')
    return render_template('search.html',
                           agents=agents,
                           search_term=search_term,
                           selected_access_level=selected_access_level,
                           dark_mode=dark_mode)


# Отправка срочного сообщения
@app.route('/send_message/<int:agent_id>', methods=['GET', 'POST'])
def send_message(agent_id):
    conn = sqlite3.connect('agents.db')
    c = conn.cursor()
    c.execute("SELECT codename, email FROM agents WHERE id=?", (agent_id,))
    agent = c.fetchone()
    conn.close()

    if not agent:
        flash('Агент не найден!', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        message = request.form.get('message', '').strip()
        if not message:
            flash('Введите текст сообщения!', 'danger')
            return redirect(url_for('send_message', agent_id=agent_id))

        # Имитация отправки сообщения
        print(f"СИМУЛЯЦИЯ ОТПРАВКИ: Сообщение для {agent[0]} ({agent[1]})")
        print(f"Текст сообщения: {message}")
        print("Сообщение успешно доставлено (имитация)")

        flash(f'Сообщение "{message[:50]}..." отправлено агенту {agent[0]} ({agent[1]})!', 'success')
        return redirect(url_for('view_agent', agent_id=agent_id))

    dark_mode = request.cookies.get('dark_mode', 'false')
    return render_template('send_message.html', agent=agent, agent_id=agent_id, dark_mode=dark_mode)


# Секретный режим - удаление всех данных
@app.route('/nuke_database', methods=['POST'])
def nuke_database():
    secret_code = request.form.get('secret_code', '').strip()

    if secret_code == 'REDACTED':
        conn = sqlite3.connect('agents.db')
        c = conn.cursor()
        c.execute("DELETE FROM agents")
        conn.commit()
        conn.close()

        flash('ВСЕ ДОСЬЕ УНИЧТОЖЕНЫ!', 'danger')
    else:
        flash('Неверный код доступа!', 'danger')

    return redirect(url_for('index'))


# Переключение темной темы
@app.route('/toggle_dark_mode')
def toggle_dark_mode():
    response = redirect(request.referrer or url_for('index'))
    current = request.cookies.get('dark_mode', 'false')
    response.set_cookie('dark_mode', 'true' if current == 'false' else 'false')
    return response


if __name__ == '__main__':
    init_db()
    app.run(debug=True)