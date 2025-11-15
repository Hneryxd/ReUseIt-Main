from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import secrets


# Guarda la base de datos DENTRO de /instance/
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reuseperu.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = secrets.token_hex(16)
# Inicializa la base de datos
db = SQLAlchemy(app)

# Creación de una tabla


class Objeto(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    contacto = db.Column(db.String(100), nullable=False)
    imagen = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    login = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(30), nullable=False)
    objetos = db.relationship('Objeto', backref='usuario', lazy=True)


# Ruta para el inicio de sesión
@app.route('/', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        form_login = request.form['email']
        form_password = request.form['password']
        user = User.query.filter_by(login=form_login, password=form_password).first()
        if user:
            session['user_id'] = user.id
            return redirect('/index')
        else:
            error = 'Nombre de usuario o contraseña incorrectos'
    return render_template('login.html', error=error)


# Ruta para el registro
@app.route('/reg', methods=['GET', 'POST'])
def reg():
    if request.method == 'POST':
        login_input = request.form['email']
        password_input = request.form['password']
        user = User(login=login_input, password=password_input)
        db.session.add(user)
        db.session.commit()
        return redirect('/')
    return render_template('register.html')


# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')


# Ruta para la página principal
@app.route('/index')
def index():
    user = User.query.get(session['user_id'])
    return render_template('index.html', user=user)


# Ruta para ver el catálogo de objetos
@app.route('/catalogo')
def catalogo():
    objetos = Objeto.query.all()
    return render_template('catalogo.html', objetos=objetos)


# Ruta para ver los detalles de un objeto
@app.route('/detalle/<int:id>')
def detalle(id):
    objeto = Objeto.query.get_or_404(id)
    return render_template('detalle.html', objeto=objeto)


# Ruta para publicar un nuevo objeto
@app.route('/publicar', methods=['GET', 'POST'])
def publicar():
    if 'user_id' not in session:
        return redirect('/')
    if request.method == 'POST':
        nuevo_objeto = Objeto(
            nombre=request.form['nombre'],
            descripcion=request.form['descripcion'],
            contacto=request.form['contacto'],
            imagen=request.form['imagen'],
            user_id=session['user_id']
        )
        db.session.add(nuevo_objeto)
        db.session.commit()
        return redirect('/catalogo')
    return render_template('publicar.html')


# Ruta para editar un objeto
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    objeto = Objeto.query.get_or_404(id)
    if 'user_id' not in session or objeto.user_id != session['user_id']:
        return "No tienes permiso para editar este objeto", 403
    if request.method == 'POST':
        objeto.nombre = request.form['nombre']
        objeto.descripcion = request.form['descripcion']
        objeto.contacto = request.form['contacto']
        objeto.imagen = request.form['imagen']
        db.session.commit()
        return redirect(f'/detalle/{id}')
    return render_template('editar.html', objeto=objeto)


# Ruta para eliminar un objeto
@app.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    objeto = Objeto.query.get_or_404(id)
    if 'user_id' not in session or objeto.user_id != session['user_id']:
        return "No tienes permiso para eliminar este objeto", 403
    db.session.delete(objeto)
    db.session.commit()
    return redirect('/catalogo')


# Ruta para ver los objetos
@app.route('/mis_objetos')
def mis_objetos():
    if 'user_id' not in session:
        return redirect('/')
    user_objetos = Objeto.query.filter_by(user_id=session['user_id']).all()
    return render_template('mis_objetos.html', objetos=user_objetos)


if __name__ == '__main__':
    app.run(debug=True)
