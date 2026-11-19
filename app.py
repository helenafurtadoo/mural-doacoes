from flask import Flask, render_template, request, redirect, url_for
from constantes import REGIOES
from models import db, Usuario
from flask_login import LoginManager
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mural.db'
app.config['SECRET_KEY'] = 'senha'
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def carregar_usuario(id_do_usuario):
    return Usuario.query.get(int(id_do_usuario))


@app.route("/")
def inicio():
    return "funcionando"


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        # .strip() remove espaços em branco no início e no final
        nome = request.form.get("nome", "").strip() # .lower() transforma o email em minúsculo
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")
        regiao = request.form.get("regiao", "").strip()
        telefone = request.form.get("telefone", "").strip()

        erro = None
        if not nome or not email or not senha or not regiao or not telefone:  # se algum campo estiver vazio
            erro = "Preencha todos os campos."

        elif len(senha) < 8:  # se a senha tiver menos de 8 caracteres
            erro = "A senha deve ter pelo menos 8 caracteres."

        elif regiao not in REGIOES:  # se a região não estiver na lista de regiões
            erro = "Escolha uma região da lista."

        else:
            # verifica se o email já está cadastrado
            existente = db.session.execute(
                db.select(Usuario).filter_by(email=email)
            ).scalar_one_or_none()
            if existente:
                erro = "Este e-mail já está cadastrado."
        if erro:
            return render_template("cadastro.html", erro=erro, regioes=REGIOES)
            
        # cria o usuário
        usuario = Usuario(nome=nome, email=email, senha_hash=generate_password_hash(senha), regiao=regiao, telefone=telefone)
        db.session.add(usuario) #.add() adiciona o usuário ao banco de dados
        db.session.commit() #.commit() salva as alterações no banco de dados
        return redirect(url_for("inicio"))  # TODO: trocar para login no passo 4
    
    return render_template("cadastro.html", regioes=REGIOES)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
