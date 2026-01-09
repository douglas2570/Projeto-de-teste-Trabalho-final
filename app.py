from flask import Flask, request, render_template_string, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'chave_super_secreta_para_testes'
app.config['DATABASE'] = 'users.db'

# --- Configuração do Banco de Dados ---
def get_db_connection():
    db_path = app.config['DATABASE']
    conn = sqlite3.connect(db_path, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    try:
        with get_db_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL
                )
            ''')
            conn.commit()
    except Exception as e:
        print(f"Erro ao iniciar DB: {e}")

# --- HTML Templates (Com suporte a erro direto) ---
login_html = """
<!DOCTYPE html>
<html>
<head><title>Login</title></head>
<body>
    <h2>Login do Sistema</h2>
    
    {% if error %}
        <div style="color: red;">{{ error }}</div>
    {% endif %}
    
    {% with messages = get_flashed_messages() %}
        {% if messages %}<div style="color: green;">{{ messages[0] }}</div>{% endif %}
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
    
    {% if error %}
        <div style="color: red;">{{ error }}</div>
    {% endif %}

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
    <h2>Bem-vindo, {{ user['name'] }}!</h2>
    <p>Seu Email: {{ user['email'] }}</p>
    <hr>
    <h3>Editar Dados</h3>
    <form method="POST" action="/edit">
        Novo Nome: <input type="text" name="name" value="{{ user['name'] }}" required><br>
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
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        with get_db_connection() as conn:
            user = conn.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password)).fetchone()
        
        if user:
            session['user_id'] = user['id']
            return redirect(url_for('dashboard'))
        else:
            # AQUI MUDOU: Passa o erro direto para a variável, não via flash
            error = 'Email ou senha incorretos'
            
    return render_template_string(login_html, error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        try:
            with get_db_connection() as conn:
                conn.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
                conn.commit()
            flash('Cadastro realizado! Faça login.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            # AQUI MUDOU: Passa o erro direto
            error = 'Erro: Este email já está cadastrado'
            return render_template_string(register_html, error=error)
        except Exception as e:
            error = f'Erro genérico: {str(e)}'
            return render_template_string(register_html, error=error)
            
    return render_template_string(register_html, error=error)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    with get_db_connection() as conn:
        user = conn.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    
    if user is None:
        session.pop('user_id', None)
        return redirect(url_for('login'))
        
    return render_template_string(dashboard_html, user=user)

@app.route('/edit', methods=['POST'])
def edit():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    name = request.form['name']
    password = request.form['password']
    
    with get_db_connection() as conn:
        if password:
            conn.execute("UPDATE users SET name = ?, password = ? WHERE id = ?", (name, password, session['user_id']))
        else:
            conn.execute("UPDATE users SET name = ? WHERE id = ?", (name, session['user_id']))
        conn.commit()
    
    return redirect(url_for('dashboard'))

@app.route('/delete')
def delete():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    with get_db_connection() as conn:
        conn.execute("DELETE FROM users WHERE id = ?", (session['user_id'],))
        conn.commit()
    
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