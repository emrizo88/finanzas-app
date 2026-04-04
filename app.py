from flask import Flask, request, redirect, url_for, render_template
from database import crear_tablas, agregar_inversion_db,eliminar_inversion_db,obtener_inversiones,eliminar_deuda,agregar_deuda,obtener_deudas, eliminar_presupuesto_db,obtener_presupuestos, agregar_presupuesto_db,actualizar_monto_gastado, obtener_transacciones, agregar_transaccion, eliminar_transaccion, obtener_resumen_mes
from datetime import date
app = Flask(__name__)
crear_tablas()

@app.route('/')
def index():
    mes_actual = date.today().strftime('%Y-%m')
    resumen = obtener_resumen_mes(mes_actual)
    return render_template("index.html", resumen=resumen,mes=mes_actual)

@app.route('/presupuestos/agregar',methods=['POST'])
def agregar_presupuesto():
    mes = request.form['mes']
    categoria = request.form['categoria']
    monto_limite = float(request.form['monto_limite'])
    agregar_presupuesto_db(mes,categoria,monto_limite)
    return redirect(url_for('presupuestos_page'))

@app.route('/presupuestos')
def presupuestos_page():
    mes_actual = date.today().strftime('%Y-%m')
    lista = obtener_presupuestos(mes_actual)
    return render_template('presupuestos.html', presupuestos=lista)



@app.route('/transacciones/agregar' , methods=['POST'])
def agregar():
    fecha = request.form['fecha']
    tipo = request.form['tipo']
    categoria = request.form['categoria']
    monto = float(request.form['monto'])
    descripcion = request.form.get('descripcion','')

    agregar_transaccion(fecha,tipo,categoria,monto,descripcion)
    if (tipo == 'gasto'):
        mes = fecha[:7]
        actualizar_monto_gastado(mes,categoria)
    return redirect(url_for('transacciones'))

@app.route('/transacciones/elminar/<int:id>',methods=['POST'])
def eliminar(id):
    eliminar_transaccion(id)
    return redirect(url_for('transacciones'))

@app.route('/presupuestos/eliminar/<int:id>',methods=['POST'])
def eliminar_presupuesto(id):
    eliminar_presupuesto_db(id)
    return redirect(url_for('presupuestos_page'))

@app.route('/deudas')
def deudas():
    lista = obtener_deudas()
    return render_template('deudas.html', deudas=lista)

@app.route('/deudas/agregar', methods=['POST'])
def agregar_deudas():
    nombre = request.form['name']
    monto_total = float(request.form['monto_total'])
    tasa_interes = request.form['tasa_interes']
    fecha_inicio = request.form['fecha_inicio']
    fecha_limite = request.form.get('fecha_limite')
    agregar_deuda(nombre,monto_total,tasa_interes,fecha_inicio,fecha_limite)
    return redirect(url_for('deudas'))

@app.route('/deudas/eliminar/<int:id>', methods=['POST'])
def eliminar_deudas(id):
    eliminar_deuda(id)
    return redirect(url_for('deudas'))

@app.route('/inversiones')
def inversiones():
    lista = obtener_inversiones()
    return render_template('inversiones.html', inversiones=lista)

@app.route('/inversiones/agregar', methods=['POST'])
def agregar_inversion():
    nombre = request.form['nombre']
    tipo = request.form['tipo']
    monto_invertido = float(request.form['monto_invertido'])
    valor_actual = float(request.form['valor_actual'])
    fecha = request.form.get('fecha')
    agregar_inversion_db(nombre,tipo,monto_invertido,valor_actual,fecha)
    return redirect(url_for('inversiones'))

@app.route('/inversiones/eliminar/<int:id>', methods=['POST'])
def eliminar_inversiones(id):
    eliminar_inversion_db(id)
    return redirect(url_for('inversiones'))



@app.route('/transacciones')
def transacciones():
    lista = obtener_transacciones()
    return render_template('transacciones.html', transacciones=lista)


if __name__ == "__main__":
    app.run(debug=True)


