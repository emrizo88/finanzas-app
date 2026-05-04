import sqlite3
from werkzeug.security import generate_password_hash

DATABASE = 'finanzas.db'

def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def obtener_resumen_mes(user_id, mes):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COALESCE(SUM(monto), 0) FROM transacciones
        WHERE tipo = 'ingreso' AND user_id = ? AND fecha LIKE ?
    ''', (user_id, f'{mes}%',))
    ingresos = cursor.fetchone()[0]
    cursor.execute('''
        SELECT COALESCE(SUM(monto), 0) FROM transacciones
        WHERE tipo = 'gasto' AND user_id = ? AND fecha LIKE ?
    ''', (user_id, f'{mes}%',))
    gastos = cursor.fetchone()[0]
    conn.close()
    return {'ingresos': ingresos, 'gastos': gastos, 'balance': ingresos - gastos}

def obtener_gastos_por_categoria(user_id,mes):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT categoria, SUM(monto) FROM transacciones 
        WHERE tipo = 'gasto' AND user_id = ? AND fecha LIKE ? GROUP BY categoria
    ''', (user_id, f'{mes}%',))
    gastos_por_categoria = cursor.fetchall()
    conn.close()
    return gastos_por_categoria

def obtener_deuda_del_mes(user_id,mes):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT nombre , monto_total, monto_pagado FROM deudas WHERE user_id = ? AND fecha_inicio <= ? AND (fecha_limite >= ? OR fecha_limite IS NULL)                 
                   ''', (user_id, f'{mes}-31', f'{mes}-01'))
    deudas_del_mes = cursor.fetchall()
    resultado = []
    for d in deudas_del_mes:
        d = dict(d)
        d['pendiente'] = d['monto_total'] - d['monto_pagado']
        resultado.append(d)
    conn.close()
    return resultado

def pagar_deuda(user_id,id,monto):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE deudas SET monto_pagado = (monto_pagado + ?) WHERE user_id = ? AND id = ?
        ''', (monto,user_id,id))
    conn.commit()
    conn.close()

def agregar_ala_deuda(user_id,id,monto):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE deudas SET monto_total = (monto_total + ?) WHERE user_id = ? AND id = ?
        ''', (monto,user_id,id))
    conn.commit()
    conn.close()
    

def obtener_transacciones(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM transacciones WHERE user_id = ? ORDER BY fecha DESC
    ''', (user_id,))
    transacciones = cursor.fetchall()
    conn.close()
    return transacciones

def agregar_transaccion(fecha, tipo, categoria, monto, descripcion, user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO transacciones (fecha, tipo, categoria, monto, descripcion, user_id)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (fecha, tipo, categoria, monto, descripcion, user_id))
    conn.commit()
    conn.close()

def eliminar_transaccion(user_id, id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM transacciones WHERE id = ? AND user_id = ?', (id, user_id))
    conn.commit()
    conn.close()

def actualizar_monto_gastado(user_id, mes, categoria):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COALESCE(SUM(monto), 0) FROM transacciones
        WHERE tipo = 'gasto' AND user_id = ? AND categoria = ? AND fecha LIKE ?
    ''', (user_id, categoria, f'{mes}%',))
    total = cursor.fetchone()[0]
    cursor.execute('''
        UPDATE presupuestos SET monto_gastado = ?
        WHERE user_id = ? AND mes = ? AND categoria = ?
    ''', (total, user_id, mes, categoria))
    conn.commit()
    conn.close()

def obtener_presupuestos(user_id, mes):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM presupuestos WHERE user_id = ? AND mes = ?
    ''', (user_id, mes))
    presupuestos = cursor.fetchall()
    resultado = []
    for p in presupuestos:
        p = dict(p)
        if p['monto_limite'] == 0:
            p['porcentaje'] = 0
        else:
            p['porcentaje'] = (p['monto_gastado'] * 100) / p['monto_limite']
        resultado.append(p)
    return resultado

def agregar_presupuesto_db(user_id, mes, categoria, monto_limite):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO presupuestos (user_id, mes, categoria, monto_limite)
        VALUES (?, ?, ?, ?)
    ''', (user_id, mes, categoria, monto_limite))
    conn.commit()
    conn.close()

def eliminar_presupuesto_db(user_id, id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM presupuestos WHERE id = ? AND user_id = ?', (id, user_id))
    conn.commit()
    conn.close()

def obtener_deudas(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM deudas WHERE user_id = ?', (user_id,))
    deudas = cursor.fetchall()
    resultado = []
    for p in deudas:
        p = dict(p)
        p['monto_pendiente'] = p['monto_total'] - p['monto_pagado']
        resultado.append(p)
    conn.close()
    return resultado

def agregar_deuda(user_id, nombre, monto_total, tasa_interes, fecha_inicio, fecha_limite):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO deudas (user_id, nombre, monto_total, tasa_interes, fecha_inicio, fecha_limite)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, nombre, monto_total, tasa_interes, fecha_inicio, fecha_limite))
    conn.commit()
    conn.close()

def eliminar_deuda(user_id, id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM deudas WHERE id = ? AND user_id = ?', (id, user_id))
    conn.commit()
    conn.close()

def obtener_inversiones(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM inversiones WHERE user_id = ?', (user_id,))
    inversiones = cursor.fetchall()
    resultado = []
    for p in inversiones:
        p = dict(p)
        p['resultado'] = p['valor_actual'] - p['monto_invertido']
        resultado.append(p)
    conn.close()
    return resultado

def agregar_inversion_db(user_id, nombre, tipo, monto_invertido, valor_actual, fecha):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO inversiones (user_id, nombre, tipo, monto_invertido, valor_actual, fecha)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, nombre, tipo, monto_invertido, valor_actual, fecha))
    conn.commit()
    conn.close()

def eliminar_inversion_db(user_id, id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM inversiones WHERE id = ? AND user_id = ?', (id, user_id))
    conn.commit()
    conn.close()

def crear_tablas():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT NOT NULL UNIQUE,
            password    TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS transacciones (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL REFERENCES users(id),
            fecha       TEXT NOT NULL,
            tipo        TEXT NOT NULL CHECK(tipo IN ('gasto', 'ingreso')),
            categoria   TEXT NOT NULL,
            monto       REAL NOT NULL,
            descripcion TEXT
        );
        CREATE TABLE IF NOT EXISTS presupuestos (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id       INTEGER NOT NULL REFERENCES users(id),
            mes           TEXT NOT NULL,
            categoria     TEXT NOT NULL,
            monto_limite  REAL NOT NULL,
            monto_gastado REAL NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS deudas (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id       INTEGER NOT NULL REFERENCES users(id),
            nombre        TEXT NOT NULL,
            monto_total   REAL NOT NULL,
            monto_pagado  REAL NOT NULL DEFAULT 0,
            tasa_interes  REAL DEFAULT 0,
            fecha_inicio  TEXT NOT NULL,
            fecha_limite  TEXT
        );
        CREATE TABLE IF NOT EXISTS inversiones (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL REFERENCES users(id),
            nombre          TEXT NOT NULL,
            tipo            TEXT NOT NULL,
            monto_invertido REAL NOT NULL,
            valor_actual    REAL NOT NULL,
            fecha           TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS historial_inversiones (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            inversion_id    INTEGER NOT NULL REFERENCES inversiones(id),
            fecha           TEXT NOT NULL,
            valor           REAL NOT NULL
        );
    ''')
    conn.commit()
    conn.close()

def registrar_usuario(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    password = generate_password_hash(password)
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
    conn.commit()
    conn.close()

def obtener_usuario(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    return cursor.fetchone()

def agregar_historial(inversion_id, fecha, valor):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO historial_inversiones (inversion_id, fecha,valor) VALUES (?, ?, ?)', (inversion_id, fecha,valor))
    conn.commit()
    conn.close()

def obtener_historial(inversion_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM historial_inversiones WHERE inversion_id = ? ORDER BY fecha DESC', (inversion_id,))
    return cursor.fetchall()

def obtener_historial_todas(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT i.nombre, h.fecha, h.valor FROM historial_inversiones h JOIN inversiones i ON h.inversion_id = i.id WHERE i.user_id = ? ORDER BY h.fecha ASC', (user_id,))
    return cursor.fetchall()

def actualizar_valor_inversion(user_id, id, valor_actual):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''  
        UPDATE inversiones SET valor_actual = ?
        WHERE id = ? AND user_id = ?
    ''', (valor_actual, id, user_id,))
    conn.commit()
    conn.close()