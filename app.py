from flask import Flask, render_template
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


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)