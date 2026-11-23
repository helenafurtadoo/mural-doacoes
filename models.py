from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()

class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    regiao = db.Column(db.String(80), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    data_criacao = db.Column(db.DateTime, nullable=False, default=datetime.now)
    doacoes = db.relationship("Doacao", back_populates="doador")

class Doacao(db.Model):
    __tablename__ = "doacoes"
    id = db.Column(db.Integer, primary_key=True)
    doador_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    estado_conservacao = db.Column(db.String(50), nullable=False)
    regiao = db.Column(db.String(80), nullable=False)
    ponto_referencia = db.Column(db.String(120), nullable=True)
    foto_caminho = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), nullable=False, default="Disponível")
    data_criacao = db.Column(db.DateTime, nullable=False, default=datetime.now)
    doador = db.relationship("Usuario", back_populates="doacoes") 