import pytest
import os
from app import app, init_db, DB_NAME

# Configuração (Fixture) para rodar antes de cada teste
@pytest.fixture
def client():
    # Configura o app para modo de teste
    app.config['TESTING'] = True
    # Usa um banco de dados separado para não sujar o original
    app.config['DATABASE'] = 'test_users.db'
    
    # Cria o banco de dados de teste
    with app.app_context():
        init_db()
        
    with app.test_client() as client:
        yield client

    # Limpeza após os testes (opcional, deletar o arquivo do banco se quiser)
    # if os.path.exists(DB_NAME):
    #     os.remove(DB_NAME)

# --- CT-01: Cadastro com Sucesso (Unitário/Integração) ---
def test_cadastro_sucesso(client):
    """
    Testa se é possivel cadastrar um usuário com dados válidos.
    Resultado Esperado: Redirecionamento (status 302) para a página de login ou mensagem de sucesso.
    """
    response = client.post('/register', data={
        'name': 'Teste User',
        'email': 'teste@email.com',
        'password': '123'
    }, follow_redirects=True)
    
    # Verifica se apareceu a mensagem de sucesso no HTML retornado
    assert b"Cadastro realizado!" in response.data

# --- CT-02: Cadastro Duplicado (Regra de Negócio) ---
def test_cadastro_duplicado(client):
    """
    Testa a regra que impede emails duplicados.
    Primeiro cadastra um usuário, depois tenta cadastrar o mesmo novamente.
    Resultado Esperado: Mensagem de erro "Este email já está cadastrado".
    """
    # 1. Cadastra o primeiro
    client.post('/register', data={
        'name': 'User Original',
        'email': 'duplo@email.com',
        'password': '123'
    })
    
    # 2. Tenta cadastrar o segundo igual
    response = client.post('/register', data={
        'name': 'User Clone',
        'email': 'duplo@email.com', # Mesmo email
        'password': '456'
    }, follow_redirects=True)
    
    # Verifica se a mensagem de erro apareceu
    assert b"Erro: Este email" in response.data

# --- CT-03: Login com Senha Incorreta (Funcional/Segurança) ---
def test_login_falha(client):
    """
    Testa a autenticação inserindo uma senha errada para um usuário existente.
    Resultado Esperado: Mensagem de erro "Email ou senha incorretos".
    """
    # 1. Cadastra o usuário corretamente
    client.post('/register', data={
        'name': 'Login User',
        'email': 'login@email.com',
        'password': 'senha_correta'
    })
    
    # 2. Tenta logar com senha errada
    response = client.post('/', data={
        'email': 'login@email.com',
        'password': 'senha_errada_aqui'
    }, follow_redirects=True)
    
    # Verifica se a mensagem de erro apareceu
    assert b"Email ou senha incorretos" in response.data