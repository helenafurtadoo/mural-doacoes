import os, uuid
from flask import Flask, render_template, request, redirect, url_for, abort
from constantes import REGIOES, CATEGORIAS, ESTADO_CONSERVACAO, EXTENSOES_FOTO
from models import db, Usuario, Doacao
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mural.db'
app.config['SECRET_KEY'] = 'senha'
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads') # Caminho absoluto para a pasta de uploads
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 # Esta em bites, acima disso, o Flask retorna 413 (Request Entity Too Large)
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


def validar_doacao(titulo, descricao, categoria, estado_conservacao, regiao, ponto_referencia):
    # Regras dos campos da doação, usadas na publicação e na edição.
    # Devolve a mensagem do primeiro erro encontrado, ou None se estiver tudo certo.
    if not titulo or not descricao or not categoria or not estado_conservacao or not regiao:
        return "Preencha todos os campos obrigatórios."
    if len(titulo) > 100:
        return "O título deve ter no máximo 100 caracteres."
    if categoria not in CATEGORIAS:
        return "Escolha uma categoria da lista."
    if estado_conservacao not in ESTADO_CONSERVACAO:
        return "Escolha um estado de conservação da lista."
    if regiao not in REGIOES:
        return "Escolha uma região da lista."
    if len(ponto_referencia) > 120:
        return "O ponto de referência deve ter no máximo 120 caracteres."
    return None


def validar_foto(arquivo):
    if arquivo is None or arquivo.filename == "":
        return "Envie uma foto da doação."
    if "." not in arquivo.filename:
        return "A foto deve ser em jpg ou png."
    extensao = arquivo.filename.rsplit(".", 1)[1].lower()
    if extensao not in EXTENSOES_FOTO:
        return "A foto deve ser em jpg ou png."
    return None


def salvar_foto(arquivo):
    pasta = app.config['UPLOAD_FOLDER']
    os.makedirs(pasta, exist_ok=True)  # cria a pasta se ainda não existir
    nome_arquivo = str(uuid.uuid4()) + "." + arquivo.filename.rsplit(".", 1)[1].lower()  # Gera um nome único para o arquivo
    caminho_arquivo = os.path.join(pasta, nome_arquivo)
    arquivo.save(caminho_arquivo)
    return "uploads/" + nome_arquivo  # Retorna o caminho relativo para a pasta static, que é onde o Flask serve arquivos estáticos porque a pasta static é a raiz dos arquivos estáticos. Assim, o caminho relativo será usado na tag <img> do HTML.


def apagar_foto(caminho_relativo):
    if caminho_relativo is None:
        return
    caminho_completo = os.path.join(app.root_path, 'static', caminho_relativo)
    try:
        os.remove(caminho_completo)
    except OSError:
        pass  # Se o arquivo não existir, não faz nada


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
        foto = request.files.get("foto")

        erro = validar_doacao(titulo, descricao, categoria, estado_conservacao, regiao, ponto_referencia)
        if not erro:
            erro = validar_foto(foto)
        if erro:
            return render_template("publicar_doacao.html", erro=erro, categorias=CATEGORIAS, estados=ESTADO_CONSERVACAO, regioes=REGIOES)

        # A foto só é salva depois que tudo passou na validação (evita arquivos órfãos)
        foto_caminho = salvar_foto(foto)
        doacao = Doacao(
            doador_id=current_user.id,
            titulo=titulo,
            descricao=descricao,
            categoria=categoria,
            estado_conservacao=estado_conservacao,
            regiao=regiao,
            ponto_referencia=ponto_referencia or None,  # Se o ponto de referência estiver vazio, armazena None
            foto_caminho=foto_caminho
        )
        db.session.add(doacao)
        db.session.commit()
        return redirect(url_for("minhas_doacoes"))

    return render_template("publicar_doacao.html", categorias=CATEGORIAS, estados=ESTADO_CONSERVACAO, regioes=REGIOES)


@app.route("/doacoes/minhas")
@login_required
def minhas_doacoes():
    # Só as doações da pessoa logada, sem as removidas, da mais nova para a mais antiga
    consulta = (
        db.select(Doacao)
        .where(Doacao.doador_id == current_user.id, Doacao.status != "removida")
        .order_by(Doacao.data_criacao.desc())
    )
    doacoes = db.session.execute(consulta).scalars().all()  # .scalars() devolve objetos Doacao, .all() junta numa lista
    return render_template("minhas_doacoes.html", doacoes=doacoes)


@app.route("/doacoes/<int:doacao_id>/editar", methods=["GET", "POST"])
@login_required
def editar_doacao(doacao_id):
    doacao = db.session.get(Doacao, doacao_id)
    # Inexistente ou de outra pessoa: 404 nos dois casos, para não revelar se a doação existe
    if doacao is None or doacao.doador_id != current_user.id:
        abort(404)
    # Só doação disponível pode ser editada (RF4)
    if doacao.status != "disponível":
        abort(403)

    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        descricao = request.form.get("descricao", "").strip()
        categoria = request.form.get("categoria", "").strip()
        estado_conservacao = request.form.get("estado_conservacao", "").strip()
        regiao = request.form.get("regiao", "").strip()
        ponto_referencia = request.form.get("ponto_referencia", "").strip()
        foto = request.files.get("foto")

        erro = validar_doacao(titulo, descricao, categoria, estado_conservacao, regiao, ponto_referencia)
        if not erro and foto and foto.filename != "":
            erro = validar_foto(foto)
            
        if erro:
            return render_template("publicar_doacao.html", erro=erro, doacao=doacao, categorias=CATEGORIAS, estados=ESTADO_CONSERVACAO, regioes=REGIOES)

        # A doação veio do banco: basta mudar os atributos e fazer commit (sem db.session.add).
        # doador_id, status e data_criacao nunca vêm do formulário.
        doacao.titulo = titulo
        doacao.descricao = descricao
        doacao.categoria = categoria
        doacao.estado_conservacao = estado_conservacao
        doacao.regiao = regiao
        doacao.ponto_referencia = ponto_referencia or None
        foto_antiga = None 
        if foto and foto.filename != "":
            foto_antiga = doacao.foto_caminho #guarda ANTES de trocar
            doacao.foto_caminho = salvar_foto(foto)
        db.session.commit()
        if foto_antiga:
            apagar_foto(foto_antiga) #apaga a foto antiga depois de salvar a nova
        return redirect(url_for("minhas_doacoes"))

    return render_template("publicar_doacao.html", doacao=doacao, categorias=CATEGORIAS, estados=ESTADO_CONSERVACAO, regioes=REGIOES)


@app.route("/doacoes/<int:doacao_id>/apagar", methods=["POST"])
@login_required
def apagar_doacao(doacao_id):
    doacao = db.session.get(Doacao, doacao_id)
    if doacao is None or doacao.doador_id != current_user.id:
        abort(404)
    if doacao.status == "removida":
        abort(404)
    if doacao.status == "reservado":
        abort(403)
    doacao.status = "removida"
    db.session.commit()
    return redirect(url_for("minhas_doacoes"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
