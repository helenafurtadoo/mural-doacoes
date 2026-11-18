from flask import Flask, render_templatee, request, redirect, url_for
from constantes import REGIOES
from models import db, Usuario
from flask_login import LoginManager 

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

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        # lê os campos, normaliza e valida
        # ...

        if erro:
            return render_template("cadastro.html", regioes=REGIOES, erro=erro)

        # cria o usuário, faz o commit
        return redirect(url_for("inicio"))  # TODO: trocar para login no passo 4

    return render_template("cadastro.html", regioes=REGIOES)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)