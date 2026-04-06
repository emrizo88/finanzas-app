import sqlite3
from werkzeug.security import generate_password_hash

DATABASE = 'finanzas.db'

def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Esto permite acceder a columnas por nombre
    return conn

def obtener_resumen_mes(mes):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT COALESCE(SUM(monto), 0) FROM transacciones
        WHERE tipo = 'ingreso' AND fecha LIKE ?
    ''', (f'{mes}%',))
    ingresos = cursor.fetchone()[0]

    cursor.execute('''
        SELECT COALESCE(SUM(monto), 0) FROM transacciones
        WHERE tipo = 'gasto' AND fecha LIKE ?
    ''', (f'{mes}%',))
    gastos = cursor.fetchone()[0]

    conn.close()

    return {
        'ingresos': ingresos,
        'gastos': gastos,
        'balance': ingresos - gastos
    }

def actualizar_monto_gastado(mes,categoria):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COALESCE(SUM(monto), 0) FROM transacciones WHERE tipo = 'gasto' AND categoria=? AND fecha LIKE ?              
    ''',(categoria,(f'{mes}%')))
    transacciones = cursor.fetchone()[0]
    cursor.execute('''
        UPDATE presupuestos SET monto_gastado = ? WHERE mes = ? AND categoria = ?              
    ''',(transacciones,mes,categoria))

    conn.commit()
    conn.close()

def obtener_presupuestos(mes):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM presupuestos WHERE mes = ?              
    ''',(mes,))
    presupuestos = cursor.fetchall()
    resultado = []
    for p in presupuestos:
        p = dict(p)
        if( p['monto_limite'] == 0):
            p['porcentaje'] = 0
        else:
            p['porcentaje'] = (p['monto_gastado'] * 100) / p['monto_limite']
        resultado.append(p)

    return resultado

def agregar_presupuesto_db(mes,categoria,monto_limite):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO presupuestos (mes,categoria,monto_limite) VALUES (?,?,?) ''', (mes,categoria,monto_limite))
    conn.commit()
    conn.close()



def obtener_transacciones():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM transacciones ORDER BY fecha DESC              
    ''')
    transacciones = cursor.fetchall()
    conn.close()
    return transacciones

def agregar_transaccion(fecha,tipo,categoria,monto,descripcion):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO transacciones (fecha,tipo,categoria,monto,descripcion) VALUES (?,?,?,?,?) ''', (fecha,tipo,categoria,monto,descripcion))
    conn.commit()
    conn.close()

def eliminar_transaccion(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM transacciones WHERE id = ?', (id,))
    conn.commit()
    conn.close()

def eliminar_presupuesto_db(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM presupuestos WHERE id = ?', (id,))
    conn.commit()
    conn.close()

def obtener_deudas():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM deudas              
    ''')
    deudas = cursor.fetchall()
    resultado = []
    for p in deudas:
        p = dict(p)
        p['monto_pendiente'] = p['monto_total']  -  p['monto_pagado']
        resultado.append(p)
    
    return resultado

def agregar_deuda(nombre, monto_total, tasa_interes, fecha_inicio, fecha_limite):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO deudas (nombre,monto_total,tasa_interes,fecha_inicio,fecha_limite) VALUES (?,?,?,?,?) ''', (nombre,monto_total,tasa_interes,fecha_inicio,fecha_limite))
    conn.commit()
    conn.close()

def eliminar_deuda(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM deudas WHERE id = ?', (id,))
    conn.commit()
    conn.close()

def obtener_inversiones():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM inversiones              
    ''')
    inversiones = cursor.fetchall()
    resultado = []
    for p in inversiones:
        p = dict(p)
        p['resultado'] = p['valor_actual']  -  p['monto_invertido']
        resultado.append(p)
    
    return resultado

def agregar_inversion_db(nombre, tipo, monto_invertido, valor_actual,fecha):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO inversiones (nombre,tipo,monto_invertido,valor_actual,fecha) VALUES (?,?,?,?,?) ''', (nombre,tipo,monto_invertido,valor_actual,fecha))
    conn.commit()
    conn.close()

def eliminar_inversion_db(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM inversiones WHERE id = ?', (id,))
    conn.commit()
    conn.close()

def crear_tablas():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS transacciones (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha       TEXT NOT NULL,
            tipo        TEXT NOT NULL CHECK(tipo IN ('gasto', 'ingreso')),
            categoria   TEXT NOT NULL,
            monto       REAL NOT NULL,
            descripcion TEXT
        );

        CREATE TABLE IF NOT EXISTS presupuestos (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            mes            TEXT NOT NULL,
            categoria      TEXT NOT NULL,
            monto_limite   REAL NOT NULL,
            monto_gastado  REAL NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS deudas (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre         TEXT NOT NULL,
            monto_total    REAL NOT NULL,
            monto_pagado   REAL NOT NULL DEFAULT 0,
            tasa_interes   REAL DEFAULT 0,
            fecha_inicio   TEXT NOT NULL,
            fecha_limite   TEXT
        );

        CREATE TABLE IF NOT EXISTS inversiones (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre           TEXT NOT NULL,
            tipo             TEXT NOT NULL,
            monto_invertido  REAL NOT NULL,
            valor_actual     REAL NOT NULL,
            fecha            TEXT NOT NULL
        );
                         
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username       TEXT NOT NULL UNIQUE,
            password        TEXT NOT NULL
        );
    ''')

    conn.commit()
    conn.close()

def registrar_usuario(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    password = generate_password_hash(password)
    cursor.execute('''
        INSERT INTO users (username,password) VALUES (?,?) ''', (username,password))
    conn.commit()
    conn.close()

def obtener_usuario(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM users WHERE username = ?               
    ''',(username,))
    users = cursor.fetchone()
    
    return users
    