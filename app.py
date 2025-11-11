import os
import random
import string
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

# --- Configuração da Aplicação ---
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'uma-chave-secreta-bem-dificil-de-adivinhar')

# --- Configuração do Banco de Dados (SQLite) ---
# Define o caminho absoluto para o arquivo do banco de dados
base_dir = os.path.abspath(os.path.dirname(__file__))
# O banco de dados será um arquivo chamado 'app.db' na raiz do projeto
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# --- Modelos de Banco de Dados (SQLAlchemy) ---
# (Os modelos são idênticos ao exemplo anterior, pois o SQLAlchemy
# abstrai a diferença entre MySQL e SQLite)

class Professor(db.Model):
    """Modelo para o Professor."""
    __tablename__ = 'professor'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    # Relacionamento com Disciplinas
    disciplinas = db.relationship('Disciplina', back_populates='professor')

    def __repr__(self):
        return f'<Professor {self.email}>'

class Aluno(db.Model):
    """Modelo para o Aluno."""
    __tablename__ = 'aluno'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    
    # Status: 'convidado' ou 'ativo'
    status = db.Column(db.String(20), nullable=False, default='convidado')
    
    # Flag para forçar a troca de senha
    primeiro_acesso = db.Column(db.Boolean, nullable=False, default=True)

    # Relacionamento com Disciplinas (Muitos-para-Muitos)
    disciplinas = db.relationship('Disciplina', secondary='aluno_disciplina', back_populates='alunos')

    def __repr__(self):
        return f'<Aluno {self.email}>'

class Disciplina(db.Model):
    """Modelo para a Disciplina."""
    __tablename__ = 'disciplina'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    
    # Chave estrangeira para Professor
    professor_id = db.Column(db.Integer, db.ForeignKey('professor.id'), nullable=False)
    
    # Relacionamentos
    professor = db.relationship('Professor', back_populates='disciplinas')
    alunos = db.relationship('Aluno', secondary='aluno_disciplina', back_populates='disciplinas')

    def __repr__(self):
        return f'<Disciplina {self.nome}>'

# Tabela de associação para Alunos e Disciplinas (Muitos-para-Muitos)
aluno_disciplina = db.Table('aluno_disciplina',
    db.Column('aluno_id', db.Integer, db.ForeignKey('aluno.id'), primary_key=True),
    db.Column('disciplina_id', db.Integer, db.ForeignKey('disciplina.id'), primary_key=True)
)

# --- Rotas da Aplicação ---
# (As rotas são idênticas ao exemplo anterior)

@app.route('/')
def index():
    """Exibe a página de login."""
    if session.get('user_id'):
        # Se já estiver logado, redireciona para o dashboard
        user_type = session.get('user_type')
        if user_type == 'professor':
            return redirect(url_for('dashboard_professor'))
        elif user_type == 'aluno':
            return redirect(url_for('dashboard_aluno'))
            
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    """Processa a tentativa de login."""
    email = request.form.get('email')
    password = request.form.get('password')
    user_type = request.form.get('user_type') # 'professor' ou 'aluno'

    if not email or not password or not user_type:
        flash('Todos os campos são obrigatórios.', 'warning')
        return redirect(url_for('index'))

    if user_type == 'professor':
        user = Professor.query.filter_by(email=email).first()
    else: # user_type == 'aluno'
        user = Aluno.query.filter_by(email=email).first()

    # Verifica se o usuário existe e a senha está correta
    if user and bcrypt.check_password_hash(user.password_hash, password):
        # Armazena dados na sessão
        session['user_id'] = user.id
        session['user_type'] = user_type
        session['nome'] = user.nome

        if user_type == 'professor':
            return redirect(url_for('dashboard_professor'))
        
        else: # user_type == 'aluno'
            # Se for o primeiro acesso, força a troca de senha
            if user.primeiro_acesso:
                flash('Este é seu primeiro acesso. Por favor, altere sua senha.', 'info')
                return redirect(url_for('mudar_senha'))
            
            # Se for convidado, ativa o aluno
            if user.status == 'convidado':
                user.status = 'ativo'
                db.session.commit()
                
            return redirect(url_for('dashboard_aluno'))

    else:
        # Falha no login
        flash('E-mail ou senha inválidos. Tente novamente.', 'danger')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    """Remove o usuário da sessão."""
    session.clear()
    flash('Você saiu do sistema.', 'success')
    return redirect(url_for('index'))

# --- Dashboards (Placeholders) ---

@app.route('/professor/dashboard')
def dashboard_professor():
    """Dashboard do professor (placeholder)."""
    if session.get('user_type') != 'professor':
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('index'))
    
    nome = session.get('nome', 'Professor')
    return f'<h1>Bem-vindo, {nome}! (Dashboard do Professor)</h1><a href="{url_for("logout")}">Sair</a>'

@app.route('/aluno/dashboard')
def dashboard_aluno():
    """Dashboard do aluno (placeholder)."""
    if session.get('user_type') != 'aluno':
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('index'))
        
    nome = session.get('nome', 'Aluno')
    return f'<h1>Bem-vindo, {nome}! (Dashboard do Aluno)</h1><a href="{url_for("logout")}">Sair</a>'

# --- Funcionalidades (Placeholders) ---

@app.route('/aluno/mudar-senha', methods=['GET', 'POST'])
def mudar_senha():
    """Página para o aluno trocar a senha no primeiro acesso."""
    if session.get('user_type') != 'aluno' or not session.get('user_id'):
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('index'))
    
    aluno = db.session.get(Aluno, session['user_id'])
    if not aluno or not aluno.primeiro_acesso:
        # Se não for mais o primeiro acesso, manda para o dashboard
        return redirect(url_for('dashboard_aluno'))

    if request.method == 'POST':
        nova_senha = request.form.get('nova_senha')
        confirm_senha = request.form.get('confirm_senha')

        if not nova_senha or len(nova_senha) < 8:
            flash('A senha deve ter no mínimo 8 caracteres.', 'warning')
            return render_template('mudar_senha.html')
        
        if nova_senha != confirm_senha:
            flash('As senhas não coincidem.', 'warning')
            return render_template('mudar_senha.html')

        # Atualiza a senha e o status
        aluno.password_hash = bcrypt.generate_password_hash(nova_senha).decode('utf-8')
        aluno.primeiro_acesso = False
        
        # Ativa o aluno, caso fosse convidado
        if aluno.status == 'convidado':
            aluno.status = 'ativo'
            
        db.session.commit()
        
        flash('Senha alterada com sucesso! Você já pode acessar seu dashboard.', 'success')
        return redirect(url_for('dashboard_aluno'))

    return render_template('mudar_senha.html') # Você precisará criar este template


@app.route('/professor/cadastrar-aluno', methods=['POST'])
def cadastrar_aluno():
    """
    Placeholder da lógica para o professor cadastrar um aluno.
    Isso seria chamado de dentro do dashboard do professor.
    """
    if session.get('user_type') != 'professor':
        return "Acesso negado", 403

    # Dados vindos de um formulário no dashboard do professor
    nome_aluno = request.form.get('nome_aluno')
    email_aluno = request.form.get('email_aluno')
    id_disciplina = request.form.get('id_disciplina')
    
    # 1. Gerar senha aleatória (8-12 dígitos)
    comprimento = random.randint(8, 12)
    senha_aleatoria = ''.join(random.choices(string.ascii_letters + string.digits, k=comprimento))
    senha_hash = bcrypt.generate_password_hash(senha_aleatoria).decode('utf-8')
    
    # 2. Criar o aluno (como convidado e primeiro_acesso=True)
    try:
        novo_aluno = Aluno(
            nome=nome_aluno,
            email=email_aluno,
            password_hash=senha_hash,
            status='convidado',
            primeiro_acesso=True
        )
        
        # 3. Associar à disciplina
        disciplina = db.session.get(Disciplina, id_disciplina)
        if disciplina:
            novo_aluno.disciplinas.append(disciplina)
        
        db.session.add(novo_aluno)
        db.session.commit()
        
        # 4. (PASSO CRÍTICO) Enviar e-mail para o aluno
        # Aqui você integraria um serviço de e-mail (ex: Flask-Mail)
        print(f"--- SIMULAÇÃO DE E-MAIL ---")
        print(f"Para: {email_aluno}")
        print(f"Assunto: Convite para a plataforma")
        print(f"Olá {nome_aluno}, você foi convidado.")
        print(f"Acesse: {url_for('index', _external=True)}")
        print(f"Sua senha temporária é: {senha_aleatoria}")
        print(f"--- FIM DA SIMULAÇÃO ---")

        flash(f'Aluno {nome_aluno} cadastrado e convidado por e-mail.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao cadastrar aluno: {e}', 'danger')

    return redirect(url_for('dashboard_professor'))


# --- Execução da Aplicação ---
if __name__ == '__main__':
    # Cria as tabelas se não existirem
    with app.app_context():
        db.create_all()
    
    # Executa a aplicação em modo de debug
    app.run(debug=True)