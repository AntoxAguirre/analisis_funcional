from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config.from_object("config.Config")
db = SQLAlchemy(app)


class Usuario(db.Model):
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    rol = db.Column(db.String(20))

class Cliente(db.Model):
    id_cliente = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    direccion = db.Column(db.String(150))
    telefono = db.Column(db.String(50))
    email = db.Column(db.String(100))

class Producto(db.Model):
    id_producto = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(100))
    precio = db.Column(db.Float)
    stock = db.Column(db.Integer)

class Factura(db.Model):
    id_factura = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey("cliente.id_cliente"))
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    total = db.Column(db.Float)
    cliente = db.relationship("Cliente", backref=db.backref("facturas", lazy=True))

class DetalleFactura(db.Model):
    id_detalle = db.Column(db.Integer, primary_key=True)
    id_factura = db.Column(db.Integer, db.ForeignKey("factura.id_factura"))
    id_producto = db.Column(db.Integer, db.ForeignKey("producto.id_producto"))
    cantidad = db.Column(db.Integer)
    precio_unitario = db.Column(db.Float)
    subtotal = db.Column(db.Float)


@app.route("/")
def index():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = Usuario.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session["usuario"] = user.nombre
            return redirect(url_for("dashboard"))
        else:
            flash("Usuario o contraseña incorrectos")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "usuario" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html")


@app.route("/clientes", methods=["GET", "POST"])
def clientes():
    if request.method == "POST":
        nombre = request.form["nombre"]
        direccion = request.form.get("direccion")
        telefono = request.form.get("telefono")
        email = request.form["email"]
        nuevo = Cliente(nombre=nombre, direccion=direccion, telefono=telefono, email=email)
        db.session.add(nuevo)
        db.session.commit()
        flash("Cliente agregado correctamente")
        return redirect(url_for("clientes"))
    clientes = Cliente.query.all()
    return render_template("clientes.html", clientes=clientes)

@app.route("/clientes/eliminar/<int:id>")
def eliminar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    db.session.delete(cliente)
    db.session.commit()
    flash("Cliente eliminado")
    return redirect(url_for("clientes"))

@app.route("/clientes/editar/<int:id>", methods=["GET", "POST"])
def editar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    if request.method == "POST":
        cliente.nombre = request.form["nombre"]
        cliente.direccion = request.form.get("direccion")
        cliente.telefono = request.form.get("telefono")
        cliente.email = request.form["email"]
        db.session.commit()
        flash("Cliente actualizado correctamente")
        return redirect(url_for("clientes"))
    return render_template("editar_cliente.html", cliente=cliente)


@app.route("/productos", methods=["GET", "POST"])
def productos():
    if request.method == "POST":
        descripcion = request.form["descripcion"]
        precio = float(request.form["precio"])
        stock = int(request.form.get("stock", 0))
        nuevo = Producto(descripcion=descripcion, precio=precio, stock=stock)
        db.session.add(nuevo)
        db.session.commit()
        flash("Producto agregado correctamente")
        return redirect(url_for("productos"))
    productos = Producto.query.all()
    return render_template("productos.html", productos=productos)

@app.route("/productos/eliminar/<int:id>")
def eliminar_producto(id):
    producto = Producto.query.get_or_404(id)
    db.session.delete(producto)
    db.session.commit()
    flash("Producto eliminado")
    return redirect(url_for("productos"))


@app.route("/facturas", methods=["GET", "POST"])
def facturas():
    if request.method == "POST":
        id_cliente = int(request.form["id_cliente"])
        id_producto = int(request.form["id_producto"])
        cantidad = int(request.form["cantidad"])
        precio = float(request.form["precio"])

        subtotal = cantidad * precio
        total = subtotal

        factura = Factura(id_cliente=id_cliente, total=total)
        db.session.add(factura)
        db.session.commit()

        detalle = DetalleFactura(
            id_factura=factura.id_factura,
            id_producto=id_producto,
            cantidad=cantidad,
            precio_unitario=precio,
            subtotal=subtotal
        )
        db.session.add(detalle)

        producto = Producto.query.get(id_producto)
        if producto:
            producto.stock = max(0, producto.stock - cantidad)

        db.session.commit()
        flash("Factura creada correctamente")
        return redirect(url_for("facturas"))

    facturas = Factura.query.all()
    clientes = Cliente.query.all()
    productos = Producto.query.all()
    return render_template("facturas.html", facturas=facturas, clientes=clientes, productos=productos)

@app.route("/productos/editar/<int:id>", methods=["GET", "POST"])
def editar_producto(id):
    producto = Producto.query.get_or_404(id)
    if request.method == "POST":
        producto.descripcion = request.form["descripcion"]
        producto.precio = float(request.form["precio"])
        producto.stock = int(request.form.get("stock", 0))
        db.session.commit()
        flash("Producto actualizado correctamente")
        return redirect(url_for("productos"))
    return render_template("editar_producto.html", producto=producto)


@app.route("/facturas/<int:id>")
def detalle_factura(id):
    factura = Factura.query.get_or_404(id)
    detalles = DetalleFactura.query.filter_by(id_factura=id).all()
    return render_template("detalle_factura.html", factura=factura, detalles=detalles)



@app.route("/reportes")
def reportes():
    cliente_nombre = request.args.get("cliente")
    desde = request.args.get("desde")
    hasta = request.args.get("hasta")

    facturas_cliente = []
    facturas_periodo = []

    if cliente_nombre:
        facturas_cliente = (Factura.query.join(Cliente)
                            .filter(Cliente.nombre.ilike(f"%{cliente_nombre}%"))
                            .all())

    if desde and hasta:
        try:
            fecha_desde = datetime.strptime(desde, "%Y-%m-%d")
            fecha_hasta = datetime.strptime(hasta, "%Y-%m-%d")
            facturas_periodo = (Factura.query
                                .filter(Factura.fecha >= fecha_desde, Factura.fecha <= fecha_hasta)
                                .all())
        except ValueError:
            flash("Formato de fecha incorrecto")

    return render_template("reportes.html",
                           facturas_cliente=facturas_cliente,
                           facturas_periodo=facturas_periodo)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        if not Usuario.query.filter_by(email="admin@admin.com").first():
            admin = Usuario(
                nombre="Administrador",
                email="admin@admin.com",
                password=generate_password_hash("1234"),
                rol="admin"
            )
            db.session.add(admin)
            db.session.commit()
    app.run(debug=True)
