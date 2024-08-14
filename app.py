from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash, generate_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo

app = Flask(__name__)

# Configuración de la base de datos MySQL
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '300803'
app.config['MYSQL_DB'] = 'DB_Medicos'

app.secret_key = 'mysecret'

mysql = MySQL(app)

# Formulario para el login
class LoginForm(FlaskForm):
    rfc = StringField('RFC', validators=[DataRequired(), Length(max=15)])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar sesión')

# Formulario para pacientes
class PatientForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=50)])
    apellido = StringField('Apellido', validators=[DataRequired(), Length(max=50)])
    edad = IntegerField('Edad', validators=[DataRequired()])
    fecha_nacimiento = DateField('Fecha de Nacimiento', format='%Y-%m-%d', validators=[DataRequired()])
    alergias = TextAreaField('Alergias')
    enfermedades_cronicas = TextAreaField('Enfermedades Crónicas')
    submit = SubmitField('Guardar Paciente')

# Formulario para diagnósticos
class DiagnosisForm(FlaskForm):
    consulta_id = IntegerField('Consulta ID', validators=[DataRequired()])
    tratamiento = TextAreaField('Tratamiento')
    sintomas = TextAreaField('Síntomas')
    diagnostico = TextAreaField('Diagnóstico')
    submit = SubmitField('Guardar Diagnóstico')

# Formulario para recetas médicas
class PrescriptionForm(FlaskForm):
    consulta_id = IntegerField('Consulta ID', validators=[DataRequired()])
    receta = TextAreaField('Receta')
    submit = SubmitField('Guardar Receta')

# Formulario para historial médico
class MedicalHistoryForm(FlaskForm):
    paciente_id = IntegerField('Paciente ID', validators=[DataRequired()])
    submit = SubmitField('Agregar Historial')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        rfc = form.rfc.data
        password = form.password.data
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM Medicos WHERE Medico_RFC = %s', [rfc])
        medico = cur.fetchone()
        if medico and check_password_hash(medico[4], password):
            session['medico_rfc'] = rfc
            flash('Inicio de sesión exitoso.')
            return redirect(url_for('dashboard'))
        else:
            flash('RFC o contraseña incorrectos.')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('medico_rfc', None)
    flash('Sesión cerrada.')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'medico_rfc' not in session:
        return redirect(url_for('login'))
    medico_rfc = session['medico_rfc']
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM Pacientes WHERE PacienteID IN (SELECT PacienteID FROM Consultas WHERE Medico_RFC = %s)', [medico_rfc])
    pacientes = cur.fetchall()
    return render_template('dashboard.html', pacientes=pacientes)

@app.route('/pacientes', methods=['GET', 'POST'])
def pacientes():
    if 'medico_rfc' not in session:
        return redirect(url_for('login'))
    form = PatientForm()
    if form.validate_on_submit():
        nombre = form.nombre.data
        apellido = form.apellido.data
        edad = form.edad.data
        fecha_nacimiento = form.fecha_nacimiento.data
        alergias = form.alergias.data
        enfermedades_cronicas = form.enfermedades_cronicas.data

        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO Pacientes (Nombre, Apellido, Edad, Fecha_Nacimiento, Alergias, Enfermedades_Cronicas) VALUES (%s, %s, %s, %s, %s, %s)', 
                     (nombre, apellido, edad, fecha_nacimiento, alergias, enfermedades_cronicas))
        mysql.connection.commit()
        flash('Paciente agregado correctamente')
        return redirect(url_for('dashboard'))
    return render_template('pacientes.html', form=form)

@app.route('/diagnosticos', methods=['GET', 'POST'])
def diagnosticos():
    if 'medico_rfc' not in session:
        return redirect(url_for('login'))
    form = DiagnosisForm()
    if form.validate_on_submit():
        consulta_id = form.consulta_id.data
        tratamiento = form.tratamiento.data
        sintomas = form.sintomas.data
        diagnostico = form.diagnostico.data

        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO Diagnosticos (ConsultaID, Tratamiento, Síntomas, Diagnostico) VALUES (%s, %s, %s, %s)', 
                     (consulta_id, tratamiento, sintomas, diagnostico))
        mysql.connection.commit()
        flash('Diagnóstico agregado correctamente')
        return redirect(url_for('dashboard'))
    return render_template('diagnosticos.html', form=form)

@app.route('/recetas', methods=['GET', 'POST'])
def recetas():
    if 'medico_rfc' not in session:
        return redirect(url_for('login'))
    form = PrescriptionForm()
    if form.validate_on_submit():
        consulta_id = form.consulta_id.data
        receta = form.receta.data

        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO Recetas_Medicas (ConsultaID, Receta) VALUES (%s, %s)', 
                     (consulta_id, receta))
        mysql.connection.commit()
        flash('Receta médica agregada correctamente')
        return redirect(url_for('dashboard'))
    return render_template('recetas.html', form=form)

@app.route('/historial', methods=['GET', 'POST'])
def historial():
    if 'medico_rfc' not in session:
        return redirect(url_for('login'))
    form = MedicalHistoryForm()
    if form.validate_on_submit():
        paciente_id = form.paciente_id.data

        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO Historial_Medico (Medico_RFC, PacienteID) VALUES (%s, %s)', 
                     (session['medico_rfc'], paciente_id))
        mysql.connection.commit()
        flash('Historial médico agregado correctamente')
        return redirect(url_for('dashboard'))
    return render_template('historial.html', form=form)

if __name__ == '__main__':
    app.run(port=3000, debug=True)
