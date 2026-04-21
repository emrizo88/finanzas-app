from flask import Flask, request, redirect, url_for, render_template, session, g
from werkzeug.security import check_password_hash
from database import crear_tablas, pagar_deuda,obtener_deuda_del_mes,obtener_gastos_por_categoria,registrar_usuario, obtener_usuario, agregar_inversion_db, eliminar_inversion_db, obtener_inversiones, eliminar_deuda, agregar_deuda, obtener_deudas, eliminar_presupuesto_db, obtener_presupuestos, agregar_presupuesto_db, actualizar_monto_gastado, obtener_transacciones, agregar_transaccion, eliminar_transaccion, obtener_resumen_mes
from datetime import date

app = Flask(__name__)
app.secret_key = 'clave_secreta_123'
crear_tablas()

@app.before_request
def verificar_sesion():
    if request.endpoint in ('login', 'register', 'static'):
        return
    if 'user_id' not in session:
        return redirect(url_for('login'))
    g.username = session.get('username')

@app.route('/')
def index():
    mes_actual = date.today().strftime('%Y-%m')
    user_id = session['user_id']
    resumen = obtener_resumen_mes(user_id, mes_actual)
    deudas_mes = obtener_deuda_del_mes(user_id,mes_actual)
    gastos_cat = obtener_gastos_por_categoria(user_id,mes_actual)
    return render_template("index.html", resumen=resumen, deudas_mes=deudas_mes,gastos_cat=gastos_cat,mes=mes_actual)

@app.route('/transacciones')
def transacciones():
    user_id = session['user_id']
    lista = obtener_transacciones(user_id)
    return render_template('transacciones.html', transacciones=lista)

@app.route('/transacciones/agregar', methods=['POST'])
def agregar():
    user_id = session['user_id']
    fecha = request.form['fecha']
    tipo = request.form['tipo']
    categoria = request.form['categoria']
    monto = float(request.form['monto'])
    descripcion = request.form.get('descripcion', '')
    agregar_transaccion(fecha, tipo, categoria, monto, descripcion, user_id)
    if tipo == 'gasto':
        mes = fecha[:7]
        actualizar_monto_gastado(user_id, mes, categoria)
    return redirect(url_for('transacciones'))

@app.route('/transacciones/elminar/<int:id>', methods=['POST'])
def eliminar(id):
    user_id = session['user_id']
    eliminar_transaccion(user_id, id)
    return redirect(url_for('transacciones'))

@app.route('/presupuestos')
def presupuestos_page():
    user_id = session['user_id']
    mes_actual = date.today().strftime('%Y-%m')
    lista = obtener_presupuestos(user_id, mes_actual)
    return render_template('presupuestos.html', presupuestos=lista)

@app.route('/presupuestos/agregar', methods=['POST'])
def agregar_presupuesto():
    user_id = session['user_id']
    mes = request.form['mes']
    categoria = request.form['categoria']
    monto_limite = float(request.form['monto_limite'])
    agregar_presupuesto_db(user_id, mes, categoria, monto_limite)
    return redirect(url_for('presupuestos_page'))

@app.route('/presupuestos/eliminar/<int:id>', methods=['POST'])
def eliminar_presupuesto(id):
    user_id = session['user_id']
    eliminar_presupuesto_db(user_id, id)
    return redirect(url_for('presupuestos_page'))

@app.route('/deudas')
def deudas():
    user_id = session['user_id']
    lista = obtener_deudas(user_id)
    return render_template('deudas.html', deudas=lista)

@app.route('/deudas/pagar/<int:id>',methods=['POST'])
def pagar_deudas(id):
    user_id = session['user_id']
    monto = float(request.form['monto'])
    pagar_deuda(user_id,id,monto)
    return redirect(url_for('deudas'))

@app.route('/deudas/agregar', methods=['POST'])
def agregar_deudas():
    user_id = session['user_id']
    nombre = request.form['nombre']
    monto_total = float(request.form['monto_total'])
    tasa_interes = float(request.form['tasa_interes'])
    fecha_inicio = request.form['fecha_inicio']
    fecha_limite = request.form.get('fecha_limite')
    agregar_deuda(user_id, nombre, monto_total, tasa_interes, fecha_inicio, fecha_limite)
    return redirect(url_for('deudas'))

@app.route('/deudas/eliminar/<int:id>', methods=['POST'])
def eliminar_deudas(id):
    user_id = session['user_id']
    eliminar_deuda(user_id, id)
    return redirect(url_for('deudas'))

@app.route('/inversiones')
def inversiones():
    user_id = session['user_id']
    lista = obtener_inversiones(user_id)
    return render_template('inversiones.html', inversiones=lista)

@app.route('/inversiones/agregar', methods=['POST'])
def agregar_inversion():
    user_id = session['user_id']
    nombre = request.form['nombre']
    tipo = request.form['tipo']
    monto_invertido = float(request.form['monto_invertido'])
    valor_actual = float(request.form['valor_actual'])
    fecha = request.form.get('fecha')
    agregar_inversion_db(user_id, nombre, tipo, monto_invertido, valor_actual, fecha)
    return redirect(url_for('inversiones'))

@app.route('/inversiones/eliminar/<int:id>', methods=['POST'])
def eliminar_inversiones(id):
    user_id = session['user_id']
    eliminar_inversion_db(user_id, id)
    return redirect(url_for('inversiones'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    username = request.form['username']
    password = request.form['password']
    user = obtener_usuario(username)
    if user is None:
        return redirect(url_for('login'))
    if check_password_hash(user['password'], password):
        session['user_id'] = user['id']
        session['username'] = user['username'] 
        return redirect(url_for('index'))
    else:
        return "Login Error: Datos Incorrectos"

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    username = request.form['username']
    password = request.form['password']
    try:
        registrar_usuario(username, password)
    except:
        return "Error: Ese usuario ya es existente."
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)