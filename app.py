from flask import Flask, render_template, request, redirect, url_for
from constantes import REGIOES, CATEGORIAS, ESTADO_CONSERVACAO
from models import db, Usuario, Doacao
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mural.db'
app.config['SECRET_KEY'] = 'senha'
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def carregar_usuario(id_do_usuario):
    return db.session.get(Usuario, int(id_do_usuario))


@app.route("/")
@login_required
def inicio():
    return render_template("inicio.html") 

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")
        usuario = db.session.execute(
            db.select(Usuario).filter_by(email=email)
        ).scalar_one_or_none()
        if usuario is not None and check_password_hash(usuario.senha_hash, senha):
            login_user(usuario)
            return redirect(url_for("inicio"))
        else:
            erro = "E-mail ou senha incorretos."
            return render_template("login.html", erro=erro)
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


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
        return redirect(url_for("login"))
    
    return render_template("cadastro.html", regioes=REGIOES)


@app.route("/doacoes/nova", methods=["GET", "POST"])
@login_required
def publicar_doacao():
    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        descricao = request.form.get("descricao", "").strip()
        categoria = request.form.get("categoria", "").strip()
        estado_conservacao = request.form.get("estado_conservacao", "").strip()
        regiao = request.form.get("regiao", "").strip()
        ponto_referencia = request.form.get("ponto_referencia", "").strip()

        erro = None
        if not titulo or not descricao or not categoria or not estado_conservacao or not regiao:
            erro = "Preencha todos os campos obrigatórios."
        elif len(titulo) > 100:
            erro = "O título deve ter no máximo 100 caracteres."
        elif categoria not in CATEGORIAS:
            erro = "Escolha uma categoria da lista."
        elif estado_conservacao not in ESTADO_CONSERVACAO:
            erro = "Escolha um estado de conservação da lista."
        elif regiao not in REGIOES:
            erro = "Escolha uma região da lista."
        elif len(ponto_referencia) > 120:
            erro = "O ponto de referência deve ter no máximo 120 caracteres."
        if erro:
            return render_template("publicar_doacao.html", erro=erro, categorias=CATEGORIAS, estados=ESTADO_CONSERVACAO, regioes=REGIOES)

        doacao = Doacao(
            doador_id=current_user.id,
            titulo=titulo,
            descricao=descricao,
            categoria=categoria,
            estado_conservacao=estado_conservacao,
            regiao=regiao,
            ponto_referencia=ponto_referencia or None  # Se o ponto de referência estiver vazio, armazena None
        )
        db.session.add(doacao)
        db.session.commit()
        return redirect(url_for("minhas_doacoes")) 

    return render_template("publicar_doacao.html", categorias=CATEGORIAS, estados=ESTADO_CONSERVACAO, regioes=REGIOES)


@app.route("/doacoes/minhas")
@login_required
def minhas_doacoes():
    consulta = db.select(Doacao).where(Doacao.doador_id == current_user.id,
     Doacao.status != "removida").order_by(Doacao.data_criacao.desc()) # current_user.id retorna o id do usuário logado, Doacao.status != "removida" filtra as doações que não foram removidas, .order_by(Doacao.data_criacao.desc()) ordena as doações da mais recente para a mais antiga
    doacoes = db.session.execute(consulta).scalars().all() #.scalars() retorna uma lista de objetos Doacao, .all() retorna todos os resultados da consulta
    return render_template("minhas_doacoes.html", doacoes=doacoes)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
