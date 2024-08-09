cREATE DATABASE DB_Medicos
use DB_Medicos

CREATE TABLE Roles (
    RolID INT AUTO_INCREMENT PRIMARY KEY,
    Nombre VARCHAR(50) NOT NULL
);

CREATE TABLE Medicos (
    Medico_RFC VARCHAR(15) PRIMARY KEY,
    Nombre VARCHAR(50) NOT NULL,
    Apellidos VARCHAR(50) NOT NULL,
    Cedula_Profesional VARCHAR(20) NOT NULL,
    Contraseña VARCHAR(100) NOT NULL,
    Correo VARCHAR(100) NOT NULL,
    RolID INT,
    FOREIGN KEY (RolID) REFERENCES Roles(RolID)
);

CREATE TABLE Pacientes (
    PacienteID INT AUTO_INCREMENT PRIMARY KEY,
    Nombre VARCHAR(50) NOT NULL,
    Apellido VARCHAR(50) NOT NULL,
    Edad INT NOT NULL,
    Fecha_Nacimiento DATE NOT NULL,
    Alergias TEXT,
    Enfermedades_Cronicas TEXT
);

CREATE TABLE Consultas (
    ConsultaID INT AUTO_INCREMENT PRIMARY KEY,
    Altura DECIMAL(5,2),
    LPM INT,
    SO DECIMAL(4,1),
    Glucosa DECIMAL(5,2),
    Peso DECIMAL(5,2),
    Fecha_Consulta DATE NOT NULL,
    PacienteID INT,
    Medico_RFC VARCHAR(15),
    FOREIGN KEY (PacienteID) REFERENCES Pacientes(PacienteID),
    FOREIGN KEY (Medico_RFC) REFERENCES Medicos(Medico_RFC)
);

CREATE TABLE Diagnosticos (
    DiagnosticoID INT AUTO_INCREMENT PRIMARY KEY,
    ConsultaID INT,
    Tratamiento TEXT,
    Síntomas TEXT,
    Diagnostico TEXT,
    FOREIGN KEY (ConsultaID) REFERENCES Consultas(ConsultaID)
);

CREATE TABLE Recetas_Medicas (
    RecetaMedicaID INT AUTO_INCREMENT PRIMARY KEY,
    ConsultaID INT,
    Receta TEXT,
    FOREIGN KEY (ConsultaID) REFERENCES Consultas(ConsultaID)
);

CREATE TABLE Historial_Medico (
    HistorialMedicoID INT AUTO_INCREMENT PRIMARY KEY,
    Medico_RFC VARCHAR(15),
    PacienteID INT,
    FOREIGN KEY (Medico_RFC) REFERENCES Medicos(Medico_RFC),
    FOREIGN KEY (PacienteID) REFERENCES Pacientes(PacienteID)
);
