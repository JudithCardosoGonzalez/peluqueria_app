from flask import Flask, render_template, request, redirect
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

def conectar_db():
    conn = sqlite3.connect('base_datos.db')
    conn.row_factory = sqlite3.Row
    return conn

from datetime import datetime

@app.route('/')
def index():
    conn = conectar_db()

    # Obtener los clientes registrados
    clientes = conn.execute('SELECT * FROM clientes').fetchall()

    # Obtener la fecha y hora actual completa (incluyendo hora, minuto, segundo)
    fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Obtener la vista que se quiere mostrar: "proximas" o "pasadas"
    ver_citas = request.args.get('ver', 'proximas')

    if ver_citas == 'pasadas':
        citas = conn.execute('''
            SELECT c.id, c.fecha, cl.nombre, c.tratamiento
            FROM citas c
            JOIN clientes cl ON c.cliente_id = cl.id
            WHERE c.fecha < ?
            ORDER BY c.fecha DESC
        ''', (fecha_actual,)).fetchall()
        titulo = "Citas Pasadas"
    else:
        citas = conn.execute('''
            SELECT c.id, c.fecha, cl.nombre, c.tratamiento
            FROM citas c
            JOIN clientes cl ON c.cliente_id = cl.id
            WHERE c.fecha >= ?
            ORDER BY c.fecha
        ''', (fecha_actual,)).fetchall()
        titulo = "Próximas Citas"

    conn.close()
    return render_template('index.html', clientes=clientes, citas=citas, titulo=titulo)


@app.route('/registrar_cliente', methods=['POST'])
def registrar_cliente():
    nombre = request.form['nombre']
    telefono = request.form['telefono']
    conn = conectar_db()
    conn.execute('INSERT INTO clientes (nombre, telefono) VALUES (?, ?)', (nombre, telefono))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/agendar_cita', methods=['POST'])
def agendar_cita():
    cliente_id = request.form['cliente_id']
    fecha_input = request.form['fecha']
    tratamiento = request.form['tratamiento']

    # Convertimos la fecha del formulario (sin segundos) y le añadimos los segundos
    fecha_formateada = datetime.strptime(fecha_input, '%Y-%m-%dT%H:%M')
    fecha_str = fecha_formateada.strftime('%Y-%m-%d %H:%M:%S')

    conn = conectar_db()
    conn.execute('INSERT INTO citas (cliente_id, fecha, tratamiento) VALUES (?, ?, ?)',
                 (cliente_id, fecha_str, tratamiento))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/eliminar_cita/<int:cita_id>', methods=['POST'])
def eliminar_cita(cita_id):
    conn = conectar_db()
    conn.execute('DELETE FROM citas WHERE id = ?', (cita_id,))
    conn.commit()
    conn.close()
    return redirect('/')


@app.route('/eliminar_cliente/<int:cliente_id>', methods=['POST'])
def eliminar_cliente(cliente_id):
    conn = conectar_db()
    # Primero eliminar las citas asociadas con ese cliente
    conn.execute('DELETE FROM citas WHERE cliente_id = ?', (cliente_id,))
    # Luego eliminar el cliente
    conn.execute('DELETE FROM clientes WHERE id = ?', (cliente_id,))
    conn.commit()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)


