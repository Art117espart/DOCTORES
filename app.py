from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

from models import Medico, Pacientes, Consulta, Diagnostico, Log

@app.route('/')
def inicio():
    return redirect(url_for('login'))

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


from app import db
from datetime import datetime

class Medico(db.Model):
    __tablename__ = 'medicos'
    Medico_RFC = db.Column(db.String(15), primary_key=True)
    Nombre = db.Column(db.String(50), nullable=False)
    Apellidos = db.Column(db.String(50), nullable=False)
    Cedula_Profesional = db.Column(db.String(20), nullable=False)
    Contraseña = db.Column(db.String(100), nullable=False)
    Correo = db.Column(db.String(100), nullable=False)
    RolID = db.Column(db.Integer, db.ForeignKey('roles.RolID'))

class Paciente(db.Model):
    __tablename__ = 'pacientes'
    PacienteID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre = db.Column(db.String(50), nullable=False)
    Apellido = db.Column(db.String(50), nullable=False)
    Edad = db.Column(db.Integer, nullable=False)
    Fecha_Nacimiento = db.Column(db.Date, nullable=False)
    Alergias = db.Column(db.Text)
    Enfermedades_Cronicas = db.Column(db.Text)

class Consulta(db.Model):
    __tablename__ = 'consultas'
    ConsultaID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Altura = db.Column(db.Numeric(5,2))
    LPM = db.Column(db.Integer)
    SO = db.Column(db.Numeric(4,1))
    Glucosa = db.Column(db.Numeric(5,2))
    Peso = db.Column(db.Numeric(5,2))
    Fecha_Consulta = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    PacienteID = db.Column(db.Integer, db.ForeignKey('pacientes.PacienteID'))
    Medico_RFC = db.Column(db.String(15), db.ForeignKey('medicos.Medico_RFC'))

class Diagnostico(db.Model):
    __tablename__ = 'diagnosticos'
    DiagnosticoID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ConsultaID = db.Column(db.Integer, db.ForeignKey('consultas.ConsultaID'))
    Tratamiento = db.Column(db.Text)
    Sintomas = db.Column(db.Text)
    Diagnostico = db.Column(db.Text)

class Log(db.Model):
    __tablename__ = 'logs'
    LogID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Action = db.Column(db.String(50), nullable=False)
    Timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    Medico_RFC = db.Column(db.String(15), db.ForeignKey('medicos.Medico_RFC'))

@app.route('/medicos')
def view_doctors():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    doctors = Medico.query.all()
    return render_template('doctors.html', doctors=doctors)

@app.route('/medicos/add', methods=['GET', 'POST'])
def add_doctor():
    if request.method == 'POST':
        new_doctor = Medico(
            Medico_RFC=request.form['Medico_RFC'],
            Nombre=request.form['Nombre'],
            Apellidos=request.form['Apellidos'],
            Cedula_Profesional=request.form['Cedula_Profesional'],
            Contraseña=bcrypt.generate_password_hash(request.form['Contraseña']).decode('utf-8'),
            Correo=request.form['Correo'],
            RolID=request.form['RolID']
        )
        db.session.add(new_doctor)
        db.session.commit()
        flash('Médico agregado exitosamente!')
        return redirect(url_for('view_doctors'))
    return render_template('add_doctor.html')



@app.route('/pacientes')
def view_patients():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    medico_rfc = session.get('medico_rfc')
    patients = Paciente.query.join(Consulta).filter_by(Medico_RFC=medico_rfc).all()
    return render_template('patients.html', patients=patients)

@app.route('/pacientes/add', methods=['GET', 'POST'])
def add_patient():
    if request.method == 'POST':
        new_patient = Paciente(
            Nombre=request.form['Nombre'],
            Apellido=request.form['Apellido'],
            Edad=request.form['Edad'],
            Fecha_Nacimiento=request.form['Fecha_Nacimiento'],
            Alergias=request.form['Alergias'],
            Enfermedades_Cronicas=request.form['Enfermedades_Cronicas']
        )
        db.session.add(new_patient)
        db.session.commit()
        flash('Paciente agregado exitosamente!')
        return redirect(url_for('view_patients'))
    return render_template('add_patient.html')


@app.route('/exploracion/<int:paciente_id>', methods=['GET', 'POST'])
def exploration(paciente_id):
    if request.method == 'POST':
        new_consulta = Consulta(
            Altura=request.form['Altura'],
            LPM=request.form['LPM'],
            SO=request.form['SO'],
            Glucosa=request.form['Glucosa'],
            Peso=request.form['Peso'],
            Fecha_Consulta=request.form['Fecha_Consulta'],
            PacienteID=paciente_id,
            Medico_RFC=session.get('medico_rfc')
        )
        db.session.add(new_consulta)
        db.session.commit()
        
        new_diagnostico = Diagnostico(
            ConsultaID=new_consulta.ConsultaID,
            Tratamiento=request.form['Tratamiento'],
            Sintomas=request.form['Sintomas'],
            Diagnostico=request.form['Diagnostico']
        )
        db.session.add(new_diagnostico)
        db.session.commit()

        flash('Exploración y diagnóstico guardados exitosamente!')
        return redirect(url_for('view_patients'))
    return render_template('exploration.html')



if __name__ == '__main__':
    app.run(debug=True)
