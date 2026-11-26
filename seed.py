import os, shutil, uuid
from app import app
from models import db, Usuario, Doacao
from constantes import REGIOES, CATEGORIAS, ESTADO_CONSERVACAO
from werkzeug.security import generate_password_hash

SENHA_TESTE = "12345678"
PASTA_FOTOS = os.path.join(app.root_path, "seed_fotos")

USUARIOS = [
    {"nome": "Ana Exemplo", "email": "ana@example.com", "regiao": "Gama", "telefone": "(61) 90000-0001"},
    {"nome": "Bruno Exemplo", "email": "bruno@example.com", "regiao": "Taguatinga", "telefone": "(61) 90000-0002"},
    {"nome": "Carla Exemplo", "email": "carla@example.com", "regiao": "Plano Piloto", "telefone": "(61) 90000-0003"},
]

DOACOES = [
    # Ana (Gama)
    {"email_doador": "ana@example.com", "titulo": "Casaco de lã", "descricao": "Tamanho M, pouco usado.",
     "categoria": "Roupas e calçados", "estado_conservacao": "seminovo", "regiao": "Gama",
     "ponto_referencia": None, "foto": "roupas.jpg", "status": "disponível"},
    {"email_doador": "ana@example.com", "titulo": "Coleção de livros infantis", "descricao": "Oito livros ilustrados, algumas capas gastas.",
     "categoria": "Livros e material escolar", "estado_conservacao": "usado com marcas de uso", "regiao": "Gama",
     "ponto_referencia": "Perto da feira", "foto": "livros.jpg", "status": "disponível"},
    {"email_doador": "ana@example.com", "titulo": "Jogo de panelas", "descricao": "Três panelas de alumínio com tampa.",
     "categoria": "Utensílios de casa", "estado_conservacao": "seminovo", "regiao": "Gama",
     "ponto_referencia": None, "foto": "utensilios.jpg", "status": "disponível"},
    {"email_doador": "ana@example.com", "titulo": "Cadeira de madeira", "descricao": "Firme, com um arranhado no assento.",
     "categoria": "Móveis", "estado_conservacao": "usado com marcas de uso", "regiao": "Gama",
     "ponto_referencia": None, "foto": "moveis.jpg", "status": "doado"},

    # Bruno (Taguatinga e Ceilândia)
    {"email_doador": "bruno@example.com", "titulo": "Tênis infantil tamanho 30", "descricao": "Usado por poucos meses.",
     "categoria": "Roupas e calçados", "estado_conservacao": "usado com marcas de uso", "regiao": "Taguatinga",
     "ponto_referencia": "Próximo ao metrô", "foto": "roupas.jpg", "status": "disponível"},
    {"email_doador": "bruno@example.com", "titulo": "Mesa de estudo", "descricao": "Mesa pequena com uma gaveta.",
     "categoria": "Móveis", "estado_conservacao": "seminovo", "regiao": "Taguatinga",
     "ponto_referencia": None, "foto": "moveis.jpg", "status": "disponível"},
    {"email_doador": "bruno@example.com", "titulo": "Caminhão de brinquedo", "descricao": "Plástico resistente, todas as rodas funcionando.",
     "categoria": "Brinquedos e itens infantis", "estado_conservacao": "usado com marcas de uso", "regiao": "Ceilândia",
     "ponto_referencia": None, "foto": "brinquedos.jpg", "status": "disponível"},
    {"email_doador": "bruno@example.com", "titulo": "Livros de matemática do ensino médio", "descricao": "Volumes 1 a 3, com anotações a lápis.",
     "categoria": "Livros e material escolar", "estado_conservacao": "usado com marcas de uso", "regiao": "Taguatinga",
     "ponto_referencia": None, "foto": "livros.jpg", "status": "removida"},

    # Carla (Plano Piloto, Águas Claras e Sobradinho)
    {"email_doador": "carla@example.com", "titulo": "Ursinho e blocos de montar", "descricao": "Kit com ursinho de pelúcia e 40 blocos.",
     "categoria": "Brinquedos e itens infantis", "estado_conservacao": "seminovo", "regiao": "Plano Piloto",
     "ponto_referencia": "Perto do mercado", "foto": "brinquedos.jpg", "status": "disponível"},
    {"email_doador": "carla@example.com", "titulo": "Travessa de vidro", "descricao": "Travessa grande, nunca usada.",
     "categoria": "Utensílios de casa", "estado_conservacao": "novo", "regiao": "Águas Claras",
     "ponto_referencia": None, "foto": "utensilios.jpg", "status": "disponível"},
    {"email_doador": "carla@example.com", "titulo": "Cadernos sem uso", "descricao": "Cinco cadernos universitários lacrados.",
     "categoria": "Livros e material escolar", "estado_conservacao": "novo", "regiao": "Plano Piloto",
     "ponto_referencia": None, "foto": "livros.jpg", "status": "disponível"},
    {"email_doador": "carla@example.com", "titulo": "Estante pequena", "descricao": "Três prateleiras, precisa de um parafuso novo.",
     "categoria": "Móveis", "estado_conservacao": "usado com marcas de uso", "regiao": "Sobradinho",
     "ponto_referencia": None, "foto": "moveis.jpg", "status": "disponível"},
]


def copiar_foto(nome_arquivo): #Ela segue a ideia da salvar_foto do app.py, mas copia de uma pasta em vez de receber um upload
    origem = os.path.join(PASTA_FOTOS, nome_arquivo)
    pasta_destino = app.config['UPLOAD_FOLDER']
    os.makedirs(pasta_destino, exist_ok=True)  # cria a pasta se ainda não existir
    extensao = os.path.splitext(nome_arquivo)[1].lower()
    nome_arquivo_destino = f"{uuid.uuid4()}{extensao}"
    shutil.copyfile(origem, os.path.join(pasta_destino, nome_arquivo_destino))
    return "uploads/" + nome_arquivo_destino


STATUS_PERMITIDOS = ["disponível", "doado", "removida"]


def validar_dados():
    # Confere TODOS os dados antes de mexer no banco: um erro de digitação para o script
    # antes de criar qualquer coisa (senão as contas seriam criadas e as doações não).
    for u in USUARIOS:
        assert u["regiao"] in REGIOES, f"Região inválida na conta {u['email']}: {u['regiao']}"
    emails = [u["email"] for u in USUARIOS]
    for d in DOACOES:
        assert d["email_doador"] in emails, f"Doador não está em USUARIOS: {d['email_doador']}"
        assert d["categoria"] in CATEGORIAS, f"Categoria inválida em '{d['titulo']}': {d['categoria']}"
        assert d["estado_conservacao"] in ESTADO_CONSERVACAO, f"Estado inválido em '{d['titulo']}': {d['estado_conservacao']}"
        assert d["regiao"] in REGIOES, f"Região inválida em '{d['titulo']}': {d['regiao']}"
        assert d["status"] in STATUS_PERMITIDOS, f"Status inválido em '{d['titulo']}': {d['status']}"
        assert os.path.exists(os.path.join(PASTA_FOTOS, d["foto"])), f"Foto não encontrada em seed_fotos/: {d['foto']}"


def popular():
    validar_dados()

    with app.app_context():
        db.create_all()  # o banco pode ainda não existir (ex.: computador pessoal)
        criados = set()  # e-mails das contas criadas NESTA execução

        # 1) Contas: pula quem já existe (por isso o script pode rodar mais de uma vez)
        for u in USUARIOS:
            existente = db.session.execute(
                db.select(Usuario).filter_by(email=u["email"])
            ).scalar_one_or_none()
            if existente:
                continue
            usuario = Usuario(
                nome=u["nome"],
                email=u["email"],
                senha_hash=generate_password_hash(SENHA_TESTE),
                regiao=u["regiao"],
                telefone=u["telefone"],
            )
            db.session.add(usuario)
            criados.add(u["email"])
        # flush: manda as contas para o banco (elas ganham id) SEM confirmar a transação.
        # Se algo falhar nas doações, nada é gravado: nem contas, nem doações.
        db.session.flush()

        # 2) Doações: só das contas criadas agora (evita duplicar)
        total_doacoes = 0
        for d in DOACOES:
            if d["email_doador"] not in criados:
                continue
            doador = db.session.execute(
                db.select(Usuario).filter_by(email=d["email_doador"])
            ).scalar_one()
            doacao = Doacao(
                doador_id=doador.id,
                titulo=d["titulo"],
                descricao=d["descricao"],
                categoria=d["categoria"],
                estado_conservacao=d["estado_conservacao"],
                regiao=d["regiao"],
                ponto_referencia=d["ponto_referencia"],
                foto_caminho=copiar_foto(d["foto"]),
                status=d["status"],
            )
            db.session.add(doacao)
            total_doacoes += 1
        db.session.commit()

        print(f"{len(criados)} contas e {total_doacoes} doações criadas.")


if __name__ == "__main__":
    popular()