from flask import *
from . import carro
import hashlib, os
from werkzeug.utils import secure_filename
from bd import *  # Importando conexion BD

@carro.route("/agregar")
def agregar():
    conexion = obtener_conexion()
    if 'correo' not in session:
        return redirect(url_for('autenticar.login'))
    else:
        
        productId = int(request.args.get('productId'))
        with conexion.cursor() as cursor:
            
            cursor.execute("SELECT id FROM usuario WHERE correo = %s", (session['correo'], ))
            usuario = cursor.fetchone()[0]
            cursor.fetchall()
            # Buscar si el producto ya está en el carrito del usuario
            cursor.execute("SELECT cantidad FROM carrito WHERE id = %s AND id_producto = %s", (usuario, productId))
            result = cursor.fetchone()
            if result:
                # Si el producto ya está en el carrito, aumentar la cantidad en 1
                cantidad = result[0] + 1
                cursor.fetchall()
                cursor.execute("UPDATE carrito SET cantidad = %s WHERE id = %s AND id_producto = %s", (cantidad, usuario, productId))
            else:
                # Si el producto no está en el carrito, agregarlo con cantidad 1
                cursor.fetchall()
                cursor.execute("INSERT INTO carrito (id, id_producto, cantidad) VALUES (%s, %s, %s)", (usuario, productId, 1))
            conexion.commit() 
            msg = "Added successfully"
            # Reducir el stock del producto en la base de datos
            cursor.execute('''UPDATE producto SET cantidad = cantidad - 1 WHERE id_producto = %s''', (productId,))                
            conexion.commit()         
            
    conexion.close()
    return redirect(url_for('cliente.homecliente'))
    
@carro.route("/carrito")
def carrito():
    conexion = obtener_conexion()
    noOfItems = 0
    conexion = obtener_conexion()
    correo = session['correo']
    cursor = conexion.cursor()
    cursor.execute("SELECT id FROM usuario WHERE correo = %s", (correo,))
    userId = cursor.fetchone()[0]
    cursor.fetchall()
    cursor.execute("SELECT count(id_producto) FROM carrito WHERE id = %s", (userId, ))
    noOfItems = cursor.fetchone()[0]    
    if 'correo' not in session:
        return redirect(url_for('autenticar.login'))
   # loggedIn, firstName, noOfItems = getLoginDetails()
    correo = session['correo']
    with conexion.cursor() as cursor:
        cursor.execute("SELECT id FROM usuario WHERE correo = %s", (correo, ))
        usuario = cursor.fetchone()[0]
        cursor.fetchall()
        cursor.execute("SELECT carrito.id, producto.id_producto, producto.nombre, producto.precio, producto.imagen, carrito.cantidad FROM producto, carrito WHERE producto.id_producto = carrito.id_producto AND carrito.id = %s", (usuario, ))
        
        productos = cursor.fetchall()
        
    totalPrice = 0
    for row in productos:
        totalPrice += row[3] * row[5]
    return render_template("cart.html", productos = productos, totalPrice=totalPrice, noOfItems=noOfItems)



@carro.route("/eliminar")
def eliminar():
    conexion = obtener_conexion()
    if 'correo' not in session:
        return redirect(url_for('autenticar.login'))
    correo = session['correo']
    productId = int(request.args.get('productId'))
    with conexion.cursor() as cursor:
        cursor.execute("SELECT id FROM usuario WHERE correo = %s", (correo, ))
        id = cursor.fetchone()[0]
        cursor.fetchall()
        try:
            # Buscar si el producto ya está en el carrito del usuario
            cursor.execute("SELECT cantidad FROM carrito WHERE id = %s AND id_producto = %s AND cantidad > 0", (id, productId))
            result = cursor.fetchone()
            if result:
                            
                cursor.execute("UPDATE carrito SET cantidad = cantidad - 1 WHERE id = %s AND id_producto = %s AND cantidad > 0", (id, productId))
                cursor.fetchall()
                conexion.commit()
                cursor.execute('''UPDATE producto SET cantidad = cantidad + 1 WHERE id_producto = %s''', (productId,))  
                cursor.fetchall()
                conexion.commit()
            else:
                 cursor.execute("DELETE FROM carrito WHERE id = %s AND id_producto = %s", (id, productId))
                 conexion.commit()

        except:
            conexion.rollback()
            msg = "error occured"
    conexion.close()
    return redirect(url_for('cliente.homecliente'))

@carro.route("/checkout")
def checkout():
    id = request.args.get('id')
    return render_template("checkout.html",id=id)


@carro.route('/pasarelacompra', methods=['POST'])
def pasarelacompra():
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    telefono = request.form['telefono']
    correo = request.form['correo']
    direccion = request.form['direccion']
    ciudad = request.form['ciudad']
    departamento = request.form['departamento']
    pais = request.form['pais']
    estado = 'pendiente'
    id_user = session['id']
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    query = "INSERT INTO pedido (nombre, apellido, telefono, correo, direccion, ciudad, departamento, pais, estado,id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    values = (nombre, apellido, telefono, correo, direccion, ciudad, departamento, pais, estado,id_user)
    cursor.execute(query, values)
    conexion.commit()
    return render_template('checkout.html',id_user=id_user)
