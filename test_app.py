import pytest
import os
from app import app, init_db

TEST_DB = "test_users_final.db"

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['DATABASE'] = TEST_DB
    
    if os.path.exists(TEST_DB):
        try: os.remove(TEST_DB)
        except: pass

    with app.app_context():
        init_db()
        
    with app.test_client() as client:
        yield client

    try:
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)
    except: pass

# CT-01
def test_cadastro_sucesso(client):
    response = client.post('/register', data={
        'name': 'Teste User', 'email': 'teste@email.com', 'password': '123'
    }, follow_redirects=True)
    assert b"Cadastro realizado!" in response.data

# CT-02
def test_cadastro_duplicado(client):
    client.post('/register', data={
        'name': 'User Original', 'email': 'duplo@email.com', 'password': '123'
    })
    response = client.post('/register', data={
        'name': 'User Clone', 'email': 'duplo@email.com', 'password': '456'
    }, follow_redirects=True)
    assert b"Erro: Este email" in response.data

# CT-03
def test_login_falha(client):
    client.post('/register', data={
        'name': 'Login User', 'email': 'login@email.com', 'password': 'senha_correta'
    })
    response = client.post('/', data={
        'email': 'login@email.com', 'password': 'senha_errada_aqui'
    }, follow_redirects=True)
    assert b"Email ou senha incorretos" in response.data