# Sistema de Gerenciamento de Usuários

Projeto prático desenvolvido para a disciplina de **Teste de Software Aplicado** do curso de Sistemas e Mídias Digitais (UFC Virtual).

## 📝 Sobre o Projeto

Este é um sistema web simples desenvolvido em **Python** utilizando o micro-framework **Flask**. 

O objetivo principal desta aplicação é servir como base ("objeto de estudo") para a execução de planos de teste, permitindo a prática de validações de formulário, regras de negócio e controle de acesso.

### Principais Funcionalidades
O sistema implementa um CRUD básico com autenticação:
* **Cadastro de Usuários:** Criação de conta com validação (não permite e-mails duplicados).
* **Autenticação (Login):** Acesso seguro via e-mail e senha.
* **Dashboard:** Área restrita onde o usuário visualiza seus dados.
* **Edição de Perfil:** Permite alterar o nome e a senha.
* **Exclusão de Conta:** Permite ao usuário remover seus próprios dados do sistema.

---

## 🚀 Como executar o projeto

Siga os passos abaixo para rodar a aplicação em sua máquina local.

### 1. Pré-requisitos
Certifique-se de ter o **Python 3.x** instalado em seu computador. 
* *O pip (gerenciador de pacotes) geralmente já vem instalado com o Python.*

### 2. Instalação das Dependências
Abra o terminal (CMD, PowerShell ou Terminal do VS Code) na pasta do projeto e execute o comando abaixo para instalar o **Flask** (para o site) e o **Pytest** (para os testes):

```bash
pip install flask pytest
```
## Executando a Aplicação
```bash
python app.py
```
Se tudo der certo, você verá uma mensagem no terminal parecida com: Running on http://127.0.0.1:5000

4. Acessando no Navegador
Abra seu navegador de preferência (Chrome, Firefox, Edge) e acesse o endereço:

http://127.0.0.1:5000
