import sqlite3
from datetime import date

def obtener_rend_inversiones(user_id, inversiones,dia_actual):
    resultado = []  
    for p in inversiones:
        p = dict(p)
        fecha = p['fecha']
        fecha = date.fromisoformat(p['fecha'])
        dias_transcurridos = (dia_actual - fecha).days
        rendimiento_total = (p['valor_actual'] - p['monto_invertido']) / p['monto_invertido']
        rendimiento_anualizado = rendimiento_total * (365 / dias_transcurridos)
        resultado.append({
            'nombre': p['nombre'],
            'monto_invertido': p['monto_invertido'],
            'rendimiento_anualizado': rendimiento_anualizado
        })
    return resultado
