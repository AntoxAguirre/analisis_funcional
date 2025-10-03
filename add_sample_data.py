from app import app, db, Usuario, Cliente, Producto
from werkzeug.security import generate_password_hash

with app.app_context():
    
    if not Usuario.query.filter_by(email="user1@mail.com").first():
        u1 = Usuario(
            nombre="Usuario Uno",
            email="user1@mail.com",
            password=generate_password_hash("1234"),
            rol="user"
        )
        db.session.add(u1)

    if not Usuario.query.filter_by(email="user2@mail.com").first():
        u2 = Usuario(
            nombre="Usuario Dos",
            email="user2@mail.com",
            password=generate_password_hash("1234"),
            rol="user"
        )
        db.session.add(u2)

   
    if not Cliente.query.filter_by(email="cliente1@mail.com").first():
        c1 = Cliente(
            nombre="Antonela Aguirre",
            direccion="Pasco 5757",
            telefono="3413307481",
            email="antoaguirre@mail.com"
        )
        db.session.add(c1)

    if not Cliente.query.filter_by(email="cliente2@mail.com").first():
        c2 = Cliente(
            nombre="Sofia",
            direccion="Perez",
            telefono="341568978",
            email="sofiap@mail.com"
        )
        db.session.add(c2)
   
    if not Producto.query.filter_by(descripcion="Producto A").first():
        p1 = Producto(descripcion="Producto A", precio=1500.0, stock=10)
        db.session.add(p1)

    if not Producto.query.filter_by(descripcion="Producto B").first():
        p2 = Producto(descripcion="Producto B", precio=2500.0, stock=5)
        db.session.add(p2)

    if not Producto.query.filter_by(descripcion="Producto C").first():
        p3 = Producto(descripcion="Producto C", precio=500.0, stock=50)
        db.session.add(p3)

    db.session.commit()
    print("✅ Datos de ejemplo agregados correctamente.")
