from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from config import Config
from datetime import datetime
import mysql.connector  # Asegúrate de que esta librería esté instalada

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

from models import Medico, Paciente, Consulta, Diagnostico, Log

@app.route('/')
def inicio():
    # Uso correcto del método connect en lugar de connector
    conn = mysql.connector.connect(
        host='mysql',  
        user='root',
        passwd='root',
        database='db'
    )
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students')  # Ajusta la consulta según tu esquema de base de datos
    resultados = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', students=resultados)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        rfc = request.form['rfc']
        contraseña = request.form['contraseña']
        medico = Medico.query.filter_by(Medico_RFC=rfc).first()
        if medico and bcrypt.check_password_hash(medico.Contraseña, contraseña):
            session['logged_in'] = True
            session['medico_rfc'] = medico.Medico_RFC
            return redirect(url_for('panel'))
        else:
            flash('RFC o Contraseña incorrectos', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión', 'success')
    return redirect(url_for('login'))

@app.route('/panel')
def panel():
    if 'logged_in' in session:
        return render_template('panel.html')
    return redirect(url_for('login'))

@app.route('/medicos')
def ver_medicos():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    medicos = Medico.query.all()
    return render_template('medicos.html', medicos=medicos)

@app.route('/medicos/agregar', methods=['GET', 'POST'])
def agregar_medico():
    if request.method == 'POST':
        nuevo_medico = Medico(
            Medico_RFC=request.form['Medico_RFC'],
            Nombre=request.form['Nombre'],
            Apellidos=request.form['Apellidos'],
            Cedula_Profesional=request.form['Cedula_Profesional'],
            Contraseña=bcrypt.generate_password_hash(request.form['Contraseña']).decode('utf-8'),
            Correo=request.form['Correo'],
            RolID=request.form['RolID']
        )
        db.session.add(nuevo_medico)
        db.session.commit()
        flash('¡Médico agregado exitosamente!')
        return redirect(url_for('ver_medicos'))
    return render_template('agregar_medico.html')

@app.route('/pacientes')
def ver_pacientes():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    medico_rfc = session.get('medico_rfc')
    pacientes = Paciente.query.join(Consulta).filter_by(Medico_RFC=medico_rfc).all()
    return render_template('pacientes.html', pacientes=pacientes)

@app.route('/pacientes/agregar', methods=['GET', 'POST'])
def agregar_paciente():
    if request.method == 'POST':
        nuevo_paciente = Paciente(
            Nombre=request.form['Nombre'],
            Apellido=request.form['Apellido'],
            Edad=request.form['Edad'],
            Fecha_Nacimiento=request.form['Fecha_Nacimiento'],
            Alergias=request.form['Alergias'],
            Enfermedades_Cronicas=request.form['Enfermedades_Cronicas']
        )
        db.session.add(nuevo_paciente)
        db.session.commit()
        flash('¡Paciente agregado exitosamente!')
        return redirect(url_for('ver_pacientes'))
    return render_template('agregar_paciente.html')

@app.route('/exploracion/<int:paciente_id>', methods=['GET', 'POST'])
def exploracion(paciente_id):
    if request.method == 'POST':
        nueva_consulta = Consulta(
            Altura=request.form['Altura'],
            LPM=request.form['LPM'],
            SO=request.form['SO'],
            Glucosa=request.form['Glucosa'],
            Peso=request.form['Peso'],
            Fecha_Consulta=request.form['Fecha_Consulta'],
            PacienteID=paciente_id,
            Medico_RFC=session.get('medico_rfc')
        )
        db.session.add(nueva_consulta)
        db.session.commit()
        
        nuevo_diagnostico = Diagnostico(
            ConsultaID=nueva_consulta.ConsultaID,
            Tratamiento=request.form['Tratamiento'],
            Sintomas=request.form['Sintomas'],
            Diagnostico=request.form['Diagnostico']
        )
        db.session.add(nuevo_diagnostico)
        db.session.commit()

        flash('¡Exploración y diagnóstico guardados exitosamente!')
        return redirect(url_for('ver_pacientes'))
    return render_template('exploracion.html')

@app.route('/mis_pacientes')
def mis_pacientes():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    medico_rfc = session['medico_rfc']
    pacientes = db.session.query(Paciente).join(Consulta).filter(Consulta.Medico_RFC == medico_rfc).all()
    return render_template('mis_pacientes.html', pacientes=pacientes)

if __name__ == '__main__':
    app.run(debug=True)
