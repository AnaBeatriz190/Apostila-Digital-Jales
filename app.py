import os
import random
import string
from flask import Flask, render_template, request, redirect, url_for, session, flash
# ### MUDANÇA: Importar as ferramentas do Flask-Login
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
# ### MUDANÇA: Importar o 'wraps' para criar decoradores customizados
from functools import wraps

# --- Configuração da Aplicação ---
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'uma-chave-secreta-bem-dificil-de-adivinhar')

# --- Configuração do Banco de Dados (SQLite) ---
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# --- MUDANÇA: Configuração do Flask-Login ---
login_manager = LoginManager(app)
# Se um usuário tentar acessar uma página protegida sem login,
# ele será redirecionado para a rota 'index' (sua página de login).
login_manager.login_view = 'index'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'info'

# --- Modelos de Banco de Dados (SQLAlchemy) ---

# ### MUDANÇA: Adicionar o 'UserMixin'
# O UserMixin dá ao seu modelo os métodos que o Flask-Login precisa
# (como 'is_authenticated', 'is_active', etc.)
class Professor(db.Model, UserMixin):
    """Modelo para o Professor."""
    __tablename__ = 'professor'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    disciplinas = db.relationship('Disciplina', back_populates='professor')

    # ### MUDANÇA: Adicionar métodos de senha e get_id
    # Isso move a lógica de senha para DENTRO do modelo, limpando as rotas.
    def set_password(self, password):
        """Gera o hash da senha."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Verifica a senha contra o hash."""
        return bcrypt.check_password_hash(self.password_hash, password)

    def get_id(self):
        """Retorna um ID único para o Flask-Login (formato: tipo-id)."""
        return f'professor-{self.id}'
    
    def __repr__(self):
        return f'<Professor {self.email}>'

# ### MUDANÇA: Adicionar o 'UserMixin'
class Aluno(db.Model, UserMixin):
    """Modelo para o Aluno."""
    __tablename__ = 'aluno'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='convidado')
    primeiro_acesso = db.Column(db.Boolean, nullable=False, default=True)
    disciplinas = db.relationship('Disciplina', secondary='aluno_disciplina', back_populates='alunos')

    # ### MUDANÇA: Adicionar métodos de senha e get_id
    def set_password(self, password):
        """Gera o hash da senha."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Verifica a senha contra o hash."""
        return bcrypt.check_password_hash(self.password_hash, password)

    def get_id(self):
        """Retorna um ID único para o Flask-Login (formato: tipo-id)."""
        return f'aluno-{self.id}'

    def __repr__(self):
        return f'<Aluno {self.email}>'

# --- (Modelos Disciplina e tabela associativa sem mudanças) ---

class Disciplina(db.Model):
    """Modelo para a Disciplina."""
    __tablename__ = 'disciplina'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey('professor.id'), nullable=False)
    professor = db.relationship('Professor', back_populates='disciplinas')
    alunos = db.relationship('Aluno', secondary='aluno_disciplina', back_populates='disciplinas')

    def __repr__(self):
        return f'<Disciplina {self.nome}>'

aluno_disciplina = db.Table('aluno_disciplina',
    db.Column('aluno_id', db.Integer, db.ForeignKey('aluno.id'), primary_key=True),
    db.Column('disciplina_id', db.Integer, db.ForeignKey('disciplina.id'), primary_key=True)
)

# --- ### MUDANÇA: User Loader Inteligente ---
# Esta é a função que o Flask-Login usa para carregar o usuário
# a partir da sessão.
@login_manager.user_loader
def load_user(user_id_string):
    """Carrega o usuário (Aluno ou Professor) com base no ID 'tipo-id'."""
    if not user_id_string or '-' not in user_id_string:
        return None
    
    try:
        user_type, user_id = user_id_string.split('-', 1)
        user_id = int(user_id)
        
        if user_type == 'aluno':
            # Nota: db.session.get é mais rápido que .query.get
            return db.session.get(Aluno, user_id)
        elif user_type == 'professor':
            return db.session.get(Professor, user_id)
    except (ValueError, TypeError):
        # Se o ID for inválido
        return None
    
    return None
    
# --- ### MUDANÇA: Decoradores de Rota Customizados ---
# Isso substitui aqueles 'if session.get(...)' feios em cada rota.
# Agora você só precisa adicionar @professor_required ou @aluno_required

def professor_required(f):
    """Garante que o usuário é um professor."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 'current_user' é fornecido pelo Flask-Login
        if not current_user.is_authenticated or not isinstance(current_user, Professor):
            flash('Acesso não autorizado. Área restrita a professores.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def aluno_required(f):
    """Garante que o usuário é um aluno."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not isinstance(current_user, Aluno):
            flash('Acesso não autorizado. Área restrita a alunos.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


# --- Rotas da Aplicação ---

@app.route('/')
def index():
    """Exibe a página de login."""
    # ### MUDANÇA: Usar 'current_user' do Flask-Login
    if current_user.is_authenticated:
        # Redireciona com base no tipo de usuário
        if isinstance(current_user, Professor):
            return redirect(url_for('dashboard_professor'))
        elif isinstance(current_user, Aluno):
            # Se ainda for primeiro acesso, força a troca de senha
            if current_user.primeiro_acesso:
                 return redirect(url_for('mudar_senha'))
            return redirect(url_for('dashboard_aluno'))
            
    return render_template('index.html') # Página de login

@app.route('/login', methods=['POST'])
def login():
    """Processa a tentativa de login."""
    # ### MUDANÇA: Se já logado, redireciona
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    email = request.form.get('email')
    password = request.form.get('password')
    user_type = request.form.get('user_type') # 'professor' ou 'aluno'

    if not email or not password or not user_type:
        flash('Todos os campos são obrigatórios.', 'warning')
        return redirect(url_for('index'))

    user = None
    if user_type == 'professor':
        user = Professor.query.filter_by(email=email).first()
    else: # user_type == 'aluno'
        user = Aluno.query.filter_by(email=email).first()

    # ### MUDANÇA: Usar o método 'check_password' do modelo
    if user and user.check_password(password):
        
        # ### MUDANÇA: Usar 'login_user' do Flask-Login
        # (O 'session' manual foi removido)
        login_user(user) # O Flask-Login cuida da sessão
        
        # O 'next' é para onde o Flask-Login quer nos mandar
        next_page = request.args.get('next')
        
        if user_type == 'professor':
            return redirect(next_page or url_for('dashboard_professor'))
        
        else: # user_type == 'aluno'
            # Se for o primeiro acesso, força a troca de senha
            if user.primeiro_acesso:
                flash('Este é seu primeiro acesso. Por favor, altere sua senha.', 'info')
                return redirect(url_for('mudar_senha'))
            
            if user.status == 'convidado':
                user.status = 'ativo'
                db.session.commit()
                
            return redirect(next_page or url_for('dashboard_aluno'))

    else:
        flash('E-mail ou senha inválidos. Tente novamente.', 'danger')
        return redirect(url_for('index'))

@app.route('/logout')
@login_required # Só pode deslogar se estiver logado
def logout():
    """Remove o usuário da sessão."""
    # ### MUDANÇA: Usar 'logout_user' do Flask-Login
    logout_user()
    flash('Você saiu do sistema.', 'success')
    return redirect(url_for('index'))

# --- Dashboards ---

@app.route('/professor/dashboard')
# ### MUDANÇA: Usar os decoradores!
# Veja como ficou mais limpo.
@login_required
@professor_required
def dashboard_professor():
    """Dashboard do professor."""
    # Não precisamos mais do 'if session.get(...)'
    # 'current_user' está disponível automaticamente
    return f'<h1>Bem-vindo, {current_user.nome}! (Dashboard do Professor)</h1><a href="{url_for("logout")}">Sair</a>'

@app.route('/aluno/dashboard')
# ### MUDANÇA: Usar os decoradores!
@login_required
@aluno_required
def dashboard_aluno():
    """Dashboard do aluno."""
    # Não precisamos mais do 'if session.get(...)'
    return f'<h1>Bem-vindo, {current_user.nome}! (Dashboard do Aluno)</h1><a href="{url_for("logout")}">Sair</a>'

# --- Funcionalidades ---

@app.route('/aluno/mudar-senha', methods=['GET', 'POST'])
# ### MUDANÇA: Usar os decoradores!
@login_required
@aluno_required
def mudar_senha():
    """Página para o aluno trocar a senha no primeiro acesso."""
    
    # ### MUDANÇA: 'aluno' agora é 'current_user'
    # 'db.session.get(Aluno, session['user_id'])' foi removido
    aluno = current_user 
    
    # Se não for mais o primeiro acesso, manda embora
    if not aluno.primeiro_acesso:
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

        # ### MUDANÇA: Usar o método 'set_password'
        aluno.set_password(nova_senha) 
        aluno.primeiro_acesso = False
        
        if aluno.status == 'convidado':
            aluno.status = 'ativo'
            
        db.session.commit()
        
        flash('Senha alterada com sucesso! Você já pode acessar seu dashboard.', 'success')
        return redirect(url_for('dashboard_aluno'))

    return render_template('mudar_senha.html') # Você precisará criar este template


@app.route('/professor/cadastrar-aluno', methods=['POST'])
# ### MUDANÇA: Usar os decoradores!
@login_required
@professor_required
def cadastrar_aluno():
    """Lógica para o professor cadastrar um aluno."""
    
    nome_aluno = request.form.get('nome_aluno')
    email_aluno = request.form.get('email_aluno')
    id_disciplina = request.form.get('id_disciplina')
    
    # Validação simples (pode melhorar)
    if not nome_aluno or not email_aluno:
         flash('Nome e e-mail do aluno são obrigatórios.', 'warning')
         return redirect(url_for('dashboard_professor'))

    # Verifica se o aluno já existe
    if Aluno.query.filter_by(email=email_aluno).first():
        flash(f'O e-mail {email_aluno} já está cadastrado.', 'warning')
        return redirect(url_for('dashboard_professor'))
        
    comprimento = random.randint(8, 12)
    senha_aleatoria = ''.join(random.choices(string.ascii_letters + string.digits, k=comprimento))
    
    try:
        novo_aluno = Aluno(
            nome=nome_aluno,
            email=email_aluno,
            status='convidado',
            primeiro_acesso=True
        )
        # ### MUDANÇA: Usar 'set_password' ao criar
        novo_aluno.set_password(senha_aleatoria)
        
        if id_disciplina:
            disciplina = db.session.get(Disciplina, int(id_disciplina))
            if disciplina:
                novo_aluno.disciplinas.append(disciplina)
        
        db.session.add(novo_aluno)
        db.session.commit()
        
        # 4. (PASSO CRÍTICO) Enviar e-mail para o aluno
        # (A simulação está ótima)
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
        # Se for um erro de e-mail único
        if 'UNIQUE constraint' in str(e):
             flash(f'O e-mail {email_aluno} já está cadastrado.', 'danger')
        else:
             flash(f'Erro ao cadastrar aluno: {e}', 'danger')

    return redirect(url_for('dashboard_professor'))


# --- Execução da Aplicação ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    app.run(debug=True)