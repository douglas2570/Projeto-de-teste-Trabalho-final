from flask import Flask, request, render_template_string, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'chave_super_secreta_para_testes' # Necessário para sessões
DB_NAME = "users.db"

# --- Configuração do Banco de Dados ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# --- HTML Templates (Simplificados para facilitar o teste) ---
login_html = """
<!DOCTYPE html>
<html>
<head><title>Login</title></head>
<body>
    <h2>Login do Sistema</h2>
    {% with messages = get_flashed_messages() %}
        {% if messages %}<div style="color: red;">{{ messages[0] }}</div>{% endif %}
    {% endwith %}
    <form method="POST" action="/">
        Email: <input type="email" name="email" required><br>
        Senha: <input type="password" name="password" required><br>
        <button type="submit">Entrar</button>
    </form>
    <br><a href="/register">Cadastrar nova conta</a>
</body>
</html>
"""

register_html = """
<!DOCTYPE html>
<html>
<head><title>Cadastro</title></head>
<body>
    <h2>Cadastro de Usuário</h2>
    {% with messages = get_flashed_messages() %}
        {% if messages %}<div style="color: red;">{{ messages[0] }}</div>{% endif %}
    {% endwith %}
    <form method="POST" action="/register">
        Nome: <input type="text" name="name" required><br>
        Email: <input type="email" name="email" required><br>
        Senha: <input type="password" name="password" required><br>
        <button type="submit">Cadastrar</button>
    </form>
    <br><a href="/">Voltar ao Login</a>
</body>
</html>
"""

dashboard_html = """
<!DOCTYPE html>
<html>
<head><title>Dashboard</title></head>
<body>
    <h2>Bem-vindo, {{ user[1] }}!</h2>
    <p>Seu Email: {{ user[2] }}</p>
    <hr>
    <h3>Editar Dados</h3>
    <form method="POST" action="/edit">
        Novo Nome: <input type="text" name="name" value="{{ user[1] }}" required><br>
        Nova Senha: <input type="password" name="password" placeholder="Nova senha"><br>
        <button type="submit">Atualizar</button>
    </form>
    <hr>
    <h3>Zona de Perigo</h3>
    <a href="/delete" onclick="return confirm('Tem certeza que deseja excluir sua conta?')"><button style="color:red;">Excluir Conta</button></a>
    <hr>
    <a href="/logout">Sair</a>
</body>
</html>
"""

# --- Rotas ---

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user[0]
            return redirect(url_for('dashboard'))
        else:
            flash('Email ou senha incorretos!')
            
    return render_template_string(login_html)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
            conn.commit()
            conn.close()
            flash('Cadastro realizado! Faça login.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Erro: Este email já está cadastrado.')
            
    return render_template_string(register_html)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],))
    user = cursor.fetchone()
    conn.close()
    
    return render_template_string(dashboard_html, user=user)

@app.route('/edit', methods=['POST'])
def edit():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    name = request.form['name']
    password = request.form['password']
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Só atualiza a senha se o usuário digitar algo novo
    if password:
        cursor.execute("UPDATE users SET name = ?, password = ? WHERE id = ?", (name, password, session['user_id']))
    else:
        cursor.execute("UPDATE users SET name = ? WHERE id = ?", (name, session['user_id']))
    conn.commit()
    conn.close()
    
    return redirect(url_for('dashboard'))

@app.route('/delete')
def delete():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (session['user_id'],))
    conn.commit()
    conn.close()
    
    session.pop('user_id', None)
    flash('Conta excluída com sucesso.')
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)