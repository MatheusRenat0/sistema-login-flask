import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = "sua_chave_secreta_aqui" 

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'login_example.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='Usuario')
    
    def __init__(self, username, senha, role='Usuario'):
        self.username = username
        self.set_senha(senha)
        self.role = role
    
    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)
    
    def check_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

@app.route('/')
def index():

    if 'authenticated' not in session:
        return redirect(url_for('login'))
    
    return f"""
    <h1>Olá, {session.get('username')}!</h1>
    <p>Você está logado com o perfil: {session.get('role')}</p>
    <a href="/logout">Sair</a>
    """

@app.route('/login', methods=['GET', 'POST'])
def login():

    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
  
        usuario = Usuario.query.filter_by(username=username).first()
    
        if usuario and usuario.check_senha(password):
          
            session['authenticated'] = True
            session['username'] = username
            session['role'] = usuario.role
            return redirect(url_for('index'))
        else:
       
            error = "Usuário ou senha inválidos. Tente novamente."
            
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    """ Remove os dados do usuário da sessão (efetua o logout). """
    session.pop('authenticated', None)
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
    
        db.create_all()
        
        if Usuario.query.count() == 0:
            print("Criando usuário de exemplo...")
            usuario_exemplo = Usuario(username='admin', senha='123', role='Administrador')
            db.session.add(usuario_exemplo)
            db.session.commit()
            print("Usuário 'admin' com senha '123' criado com sucesso!")

    app.run(debug=True)