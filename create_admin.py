import sys
from getpass import getpass
from app import app, db, Professor

def create_admin():
    """
    Script de linha de comando para criar o primeiro professor (admin).
    """
    print("--- Criar Conta de Professor Admin ---")
    
    # Executa dentro do contexto da aplicação Flask
    with app.app_context():
        # 1. Obter informações
        nome = input("Nome do Professor: ").strip()
        email = input("Email do Professor: ").strip().lower()
        
        # 2. Verificar se o e-mail já existe
        existing_user = Professor.query.filter_by(email=email).first()
        if existing_user:
            print(f"Erro: Um professor com o email '{email}' já existe.")
            return

        # 3. Obter a senha de forma segura
        password = getpass("Digite a senha (mín. 8 caracteres): ")
        if not password or len(password) < 8:
            print("Erro: Senha muito curta. Operação cancelada.")
            return
            
        password_confirm = getpass("Confirme a senha: ")
        if password != password_confirm:
            print("Erro: As senhas não coincidem. Operação cancelada.")
            return

        # 4. Criar o novo professor
        try:
            admin_professor = Professor(
                nome=nome,
                email=email
            )
            admin_professor.set_password(password) # Usa o método do modelo
            
            db.session.add(admin_professor)
            db.session.commit()
            
            print(f"\nSucesso! Professor '{nome}' ({email}) criado.")
            print("Você já pode rodar 'python app_refatorado.py' e fazer login.")

        except Exception as e:
            db.session.rollback()
            print(f"\nErro ao criar professor: {e}")
            print("Verifique se o banco de dados 'app.db' existe.")
            print("Se não existir, rode 'python app_refatorado.py' primeiro para criá-lo e tente novamente.")

if __name__ == '__main__':
    # Garante que o banco de dados exista antes de tentar usá-lo
    with app.app_context():
        db.create_all()
        
    create_admin()