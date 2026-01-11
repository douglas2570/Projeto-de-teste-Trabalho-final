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

# --- HTML Templates  ---

# Estilo Base (CSS)
base_style = """
<style>
    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f0f2f5; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
    .container { background-color: white; padding: 2rem; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); width: 100%; max-width: 350px; }
    h2 { text-align: center; color: #333; margin-bottom: 1.5rem; }
    input { width: 100%; padding: 10px; margin: 8px 0; display: inline-block; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
    button { width: 100%; background-color: #4CAF50; color: white; padding: 12px 20px; margin: 8px 0; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; transition: background 0.3s; }
    button:hover { background-color: #45a049; }
    .btn-danger { background-color: #f44336; }
    .btn-danger:hover { background-color: #d32f2f; }
    .alert { padding: 10px; border-radius: 4px; margin-bottom: 15px; text-align: center; font-size: 0.9rem; }
    .alert-error { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    .alert-success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
    a { display: block; text-align: center; margin-top: 10px; color: #007bff; text-decoration: none; }
    a:hover { text-decoration: underline; }
    label { font-size: 0.9rem; color: #666; font-weight: bold; margin-top: 10px; display: block; }
</style>
"""

login_html = f"""
<!DOCTYPE html>
<html>
<head><title>Login</title>{base_style}</head>
<body>
    <div class="container">
        <h2>Login do Sistema</h2>
        
        {{% if error %}}
            <div class="alert alert-error">{{{{ error }}}}</div>
        {{% endif %}}
        
        {{% with messages = get_flashed_messages() %}}
            {{% if messages %}}<div class="alert alert-success">{{{{ messages[0] }}}}</div>{{% endif %}}
        {{% endwith %}}

        <form method="POST" action="/">
            <label>Email</label>
            <input type="email" name="email" placeholder="exemplo@email.com" required>
            
            <label>Senha</label>
            <input type="password" name="password" placeholder="Sua senha" required>
            
            <button type="submit">Entrar</button>
        </form>
        <a href="/register">Criar nova conta</a>
    </div>
</body>
</html>
"""

register_html = f"""
<!DOCTYPE html>
<html>
<head><title>Cadastro</title>{base_style}</head>
<body>
    <div class="container">
        <h2>Criar Conta</h2>
        
        {{% if error %}}
            <div class="alert alert-error">{{{{ error }}}}</div>
        {{% endif %}}

        <form method="POST" action="/register">
            <label>Nome Completo</label>
            <input type="text" name="name" placeholder="Seu nome" required>
            
            <label>Email</label>
            <input type="email" name="email" placeholder="exemplo@email.com" required>
            
            <label>Senha</label>
            <input type="password" name="password" placeholder="Crie uma senha" required>
            
            <button type="submit">Cadastrar</button>
        </form>
        <a href="/">Já tenho conta (Login)</a>
    </div>
</body>
</html>
"""

dashboard_html = f"""
<!DOCTYPE html>
<html>
<head><title>Dashboard</title>{base_style}</head>
<body>
    <div class="container">
        <h2>Olá, {{{{ user['name'] }}}}!</h2>
        <p style="text-align:center; color:#666;">Logado como: <strong>{{{{ user['email'] }}}}</strong></p>
        <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
        
        <h3 style="text-align:center; color:#333;">Editar Perfil</h3>
        <form method="POST" action="/edit">
            <label>Alterar Nome</label>
            <input type="text" name="name" value="{{{{ user['name'] }}}}" required>
            
            <label>Alterar Senha (Opcional)</label>
            <input type="password" name="password" placeholder="Nova senha (deixe em branco para manter)">
            
            <button type="submit" style="background-color: #2196F3;">Atualizar Dados</button>
        </form>
        
        <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
        
        <a href="/delete" onclick="return confirm('Tem certeza? Essa ação não pode ser desfeita!')">
            <button class="btn-danger">Excluir Minha Conta</button>
        </a>
        <a href="/logout" style="color: #666;">Sair do Sistema</a>
    </div>
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