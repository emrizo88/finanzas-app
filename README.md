# 💰 Mis Finanzas

Aplicación web personal de finanzas construida con Python y Flask. Permite trackear ingresos, gastos, presupuestos, deudas e inversiones con soporte multi-usuario.

## 🌐 Demo

[emrizo88.pythonanywhere.com](https://emrizo88.pythonanywhere.com)

---

## ✨ Funcionalidades

- **Dashboard** — resumen mensual de ingresos, gastos y balance con gráficas interactivas
- **Transacciones** — registro de gastos e ingresos por categoría
- **Presupuestos** — límites de gasto por categoría con barra de progreso
- **Deudas** — seguimiento de deudas con registro de pagos y cargos
- **Inversiones** — portafolio de inversiones con cálculo de rendimiento anualizado e historial de valores
- **Autenticación** — registro e inicio de sesión con contraseñas hasheadas
- **Multi-usuario** — cada usuario ve únicamente sus propios datos
- **Responsive** — adaptado para uso en iPhone y dispositivos móviles

---

## 🛠️ Stack

- **Backend** — Python, Flask
- **Base de datos** — SQLite
- **Frontend** — HTML, CSS, Bootstrap 5, Chart.js
- **Deploy** — PythonAnywhere

---

## 📁 Estructura del proyecto

```
finanzas-app/
├── app.py              # Rutas y lógica de Flask
├── database.py         # Funciones de base de datos
├── utils.py            # Cálculos financieros
├── requirements.txt    # Dependencias
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── transacciones.html
│   ├── presupuestos.html
│   ├── deudas.html
│   ├── inversiones.html
│   ├── login.html
│   └── register.html
│
└── static/
    └── css/
        └── style.css
```

---

## 🗄️ Base de datos

El proyecto usa SQLite con las siguientes tablas:

- `users` — usuarios registrados
- `transacciones` — ingresos y gastos
- `presupuestos` — límites de gasto por categoría y mes
- `deudas` — deudas con seguimiento de pagos
- `inversiones` — portafolio de inversiones
- `historial_inversiones` — historial de valores por inversión

---

## 🚀 Instalación local

```bash
# Clona el repositorio
git clone https://github.com/emrizo88/finanzas-app.git
cd finanzas-app

# Crea el entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instala dependencias
pip install -r requirements.txt

# Corre la app
python app.py
```

Abre `http://127.0.0.1:5000` en tu navegador.

---

## 👤 Autor

**Emilio Rizo**
GitHub: [@emrizo88](https://github.com/emrizo88)
