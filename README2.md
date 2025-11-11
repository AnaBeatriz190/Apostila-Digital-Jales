Projeto Base - Plataforma de Ensino (Flask + SQLite + Bootstrap)

Este é o código base para uma plataforma de ensino, conforme solicitado. Ele inclui um backend Flask, conexão com SQLite, e um frontend Bootstrap para a página de login.

Tecnologias

Backend: Flask

Banco de Dados: SQLite (conectado via Flask-SQLAlchemy)

Frontend: Bootstrap 5.3 (via CDN)

Versionamento: Git

Setup do Projeto

Siga estes passos para configurar e rodar o projeto localmente.

1. Versionamento (Git)

Se você ainda não o fez, inicialize o repositório Git:

# Navegue até a pasta do seu projeto
git init
git add .
git commit -m "Commit inicial: Estrutura base com Flask e SQLite"

# (Opcional) Conecte a um repositório remoto (ex: GitHub)
# git remote add origin [https://github.com/seu-usuario/seu-repositorio.git](https://github.com/seu-usuario/seu-repositorio.git)
# git push -u origin main


2. Configuração do Banco de Dados (SQLite)

Nenhuma configuração manual é necessária!

O banco de dados (o arquivo app.db) será criado automaticamente no diretório principal do projeto na primeira vez que você executar o app.py.

3. Configuração do Ambiente Python

É altamente recomendado usar um ambiente virtual (venv):

# 1. Crie o ambiente virtual
python -m venv venv

# 2. Ative o ambiente
# Windows (PowerShell):
# .\venv\Scripts\Activate.ps1
# Windows (CMD):
# .\venv\Scripts\activate.bat
# macOS/Linux:
# source venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt


4. Rodar a Aplicação

Com o ambiente ativado e as dependências instaladas, rode o Flask:

flask --app app --debug run
# Ou, se o if __name__ == '__main__': estiver sendo usado:
# python app.py


A aplicação estará disponível em http://127.0.0.1:5000.

Nota sobre o Professor: Como não há mais um script SQL para inserir o professor "admin", você precisará adicioná-lo manualmente na primeira execução (por exemplo, criando uma rota de "primeira-configuração" ou usando o shell do Flask).