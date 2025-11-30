import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

const GestionDatos = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('aulas'); // 'profesores', 'aulas', 'alumnos', 'cursos'
  
  // Listas para los Selects (Dropdowns)
  const [profesores, setProfesores] = useState([]);
  const [aulas, setAulas] = useState([]);
  const [grados, setGrados] = useState([]);
  const [anios, setAnios] = useState([]);
  const [asignaturas, setAsignaturas] = useState([]);

  // Cargar datos necesarios al inicio
  useEffect(() => {
    cargarListas();
  }, []);

  const cargarListas = async () => {
    try {
      const normalizeList = (data) => {
        if (!data) return [];
        if (Array.isArray(data)) return data;
        if (data && Array.isArray(data.results)) return data.results;
        // sometimes backend returns { count: N } or other shapes — fallback to empty
        return [];
      };

      const resProf = await api.get('profesores/');
      setProfesores(normalizeList(resProf.data));
      const resAulas = await api.get('aulas/');
      setAulas(normalizeList(resAulas.data));
      const resGrados = await api.get('grados/');
      setGrados(normalizeList(resGrados.data));
      const resAnios = await api.get('anios/');
      setAnios(normalizeList(resAnios.data));
      const resAsign = await api.get('asignaturas/');
      setAsignaturas(normalizeList(resAsign.data));
    } catch (error) {
      console.error("Error cargando listas", error);
    }
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: '#f9fafb', fontFamily: 'sans-serif' }}>
      
      {/* SIDEBAR SIMPLE */}
      <div style={{ width: '250px', background: '#0F6236', padding: '20px', color: 'white' }}>
        <h3>Gestión de Datos</h3>
        <p style={{fontSize: '0.8rem', opacity: 0.8}}>Panel Administrativo</p>
        <hr style={{borderColor: 'rgba(255,255,255,0.2)'}}/>
        
        <ul style={{ listStyle: 'none', padding: 0 }}>
          <li onClick={() => setActiveTab('profesores')} style={estiloMenu(activeTab === 'profesores')}>Profesores</li>
          <li onClick={() => setActiveTab('aulas')} style={estiloMenu(activeTab === 'aulas')}>Aulas y Tutores</li>
          <li onClick={() => setActiveTab('alumnos')} style={estiloMenu(activeTab === 'alumnos')}>Alumnos</li>
          <li onClick={() => setActiveTab('cursos')} style={estiloMenu(activeTab === 'cursos')}>Asignar Cursos</li>
        </ul>

        <button onClick={() => navigate('/admin')} style={{ marginTop: '50px', background: 'white', color: '#0F6236', border: 'none', padding: '10px', width: '100%', borderRadius: '5px', cursor: 'pointer', fontWeight: 'bold' }}>
          ← Volver al Dashboard
        </button>
      </div>

      {/* CONTENIDO PRINCIPAL */}
      <div style={{ flex: 1, padding: '40px' }}>
          {activeTab === 'profesores' && <FormProfesores recargar={cargarListas} />}
          {activeTab === 'aulas' && <FormAulas profesores={profesores} grados={grados} anios={anios} recargar={cargarListas} />}
          {activeTab === 'alumnos' && <FormAlumnos aulas={aulas} />}
          {activeTab === 'cursos' && <FormCursos aulas={aulas} profesores={profesores} asignaturas={asignaturas} />}
      </div>
    </div>
  );
};

// --- SUB-COMPONENTES (FORMULARIOS) ---

const FormProfesores = ({ recargar }) => {
  const [form, setForm] = useState({ nombres: '', apellidos: '', dni: '', correo: '', password: '' });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post('profesores/', form);
      console.log("Profesor registrado correctamente");
      // clear all fields including password to avoid browser suggestions
      setForm({ nombres: '', apellidos: '', dni: '', correo: '', password: '' });
      recargar();
    } catch (error) {
      alert("Error registrando profesor. Verifique que el DNI no exista.");
    }
  };

  return (
    <div>
      <h2 style={{color: '#1f2937'}}>Registrar Nuevo Profesor</h2>
      <form onSubmit={handleSubmit} style={estiloForm} autoComplete="off">
        <input placeholder="Nombres" required className="input-field" value={form.nombres} onChange={e => setForm({...form, nombres: e.target.value})} />
        <input placeholder="Apellidos" required className="input-field" value={form.apellidos} onChange={e => setForm({...form, apellidos: e.target.value})} />
        <input placeholder="DNI" required className="input-field" value={form.dni} onChange={e => setForm({...form, dni: e.target.value})} />
        <input placeholder="Correo" className="input-field" autoComplete="off" value={form.correo} onChange={e => setForm({...form, correo: e.target.value})} />
        <input placeholder="Contraseña" required type="password" className="input-field" autoComplete="new-password" value={form.password} onChange={e => setForm({...form, password: e.target.value})} />
        <button type="submit" className="btn-primary">Guardar Profesor</button>
      </form>
    </div>
  );
};
const FormAulas = ({ profesores, grados, anios, recargar }) => {
  const [form, setForm] = useState({ nombre_seccion: '', grado: '', anio_academico: '', tutor: '' });

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validación mínima en frontend
    if (!form.nombre_seccion || !form.grado || !form.anio_academico) {
      alert('Completa Sección, Grado y Año académico.');
      return;
    }

    // Convertir strings a enteros para evitar Invalid pk ""
    const payload = {
      nombre_seccion: form.nombre_seccion,
      grado: Number(form.grado) || null,
      anio_academico: Number(form.anio_academico) || null,
      tutor: form.tutor ? Number(form.tutor) : null
    };

    try {
      const res = await api.post('aulas/', payload);
      console.log('Aula creada:', res.data);
      setForm({ nombre_seccion: '', grado: '', anio_academico: '', tutor: '' });
      recargar();
    } catch (error) {
      console.error('Error creando aula:', error);
      const detail = error?.response?.data || error?.message || String(error);
      if (typeof detail === 'object') {
        alert('Error creando aula. Respuesta del servidor: ' + JSON.stringify(detail));
      } else {
        alert('Error creando aula: ' + detail + '. Revisa la consola para más detalle.');
      }
    }
  };

  return (
    <div>
      <h2 style={{color: '#1f2937'}}>Crear Aula y Asignar Tutor</h2>
        <p style={{fontSize: '0.9rem', color: '#666'}}>Selecciona el Grado y el Año académico disponibles.</p>
      <form onSubmit={handleSubmit} style={estiloForm}>
        <input placeholder="Sección (Ej: A, B, Única)" required className="input-field" value={form.nombre_seccion} onChange={e => setForm({...form, nombre_seccion: e.target.value})} />
        <select className="input-field" required value={form.grado} onChange={e => setForm({...form, grado: e.target.value})}>
          <option value="">-- Seleccionar Grado --</option>
          {grados.map(g => (
            <option key={g.id} value={g.id}>{g.nombre} - {g.nivel}</option>
          ))}
        </select>

        <select className="input-field" required value={form.anio_academico} onChange={e => setForm({...form, anio_academico: e.target.value})}>
          <option value="">-- Seleccionar Año Académico --</option>
          {anios.map(a => (
            <option key={a.id} value={a.id}>{a.anio}</option>
          ))}
        </select>

        <select className="input-field" value={form.tutor} onChange={e => setForm({...form, tutor: e.target.value})}>
            <option value="">-- Seleccionar Tutor --</option>
            {profesores.map(p => (
                <option key={p.id} value={p.id}>{p.nombres} {p.apellidos}</option>
            ))}
        </select>

        <button type="submit" className="btn-primary">Crear Aula</button>
      </form>
    </div>
  );
};

const FormAlumnos = ({ aulas }) => {
  const [form, setForm] = useState({ nombres: '', apellidos: '', dni: '', aula_actual: '' });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
    await api.post('alumnos/', form);
    console.log("Alumno matriculado correctamente");
      setForm({ ...form, nombres: '', apellidos: '', dni: '' }); // Limpiamos campos menos el aula
    } catch (error) {
      alert("Error registrando alumno");
    }
  };

  return (
    <div>
      <h2 style={{color: '#1f2937'}}>Matricular Alumno</h2>
      <form onSubmit={handleSubmit} style={estiloForm}>
        <select className="input-field" required value={form.aula_actual} onChange={e => setForm({...form, aula_actual: e.target.value})}>
            <option value="">-- Seleccionar Aula --</option>
            {aulas.map(a => (
                <option key={a.id} value={a.id}>{a.grado_nombre} - Sección "{a.nombre_seccion}"</option>
            ))}
        </select>

        <input placeholder="Nombres" required className="input-field" value={form.nombres} onChange={e => setForm({...form, nombres: e.target.value})} />
        <input placeholder="Apellidos" required className="input-field" value={form.apellidos} onChange={e => setForm({...form, apellidos: e.target.value})} />
        <input placeholder="DNI" required className="input-field" value={form.dni} onChange={e => setForm({...form, dni: e.target.value})} />
        
        <button type="submit" className="btn-primary">Registrar Alumno</button>
      </form>
    </div>
  );
};

const FormCursos = ({ aulas, profesores, asignaturas }) => {
  // Seleccionar una asignatura existente y asignarla
  const [asignacion, setAsignacion] = useState({ aula: '', profesor: '', asignatura: '' });

  const handleSubmit = async (e) => {
    e.preventDefault();
      try {
      await api.post('cursos-asignados/', {
        aula: asignacion.aula,
        profesor: asignacion.profesor,
        asignatura: asignacion.asignatura
      });

      console.log("Curso asignado al profesor");
      setAsignacion({ aula: '', profesor: '', asignatura: '' });
    } catch (error) {
      console.error(error);
      alert("Error asignando curso. Revisa la consola.");
    }
  };

  return (
    <div>
      <h2 style={{color: '#1f2937'}}>Asignar Asignatura a Profesor</h2>
      <form onSubmit={handleSubmit} style={estiloForm}>
        <label>Seleccionar Asignatura:</label>
        <select className="input-field" required value={asignacion.asignatura} onChange={e => setAsignacion({...asignacion, asignatura: e.target.value})}>
          <option value="">-- Seleccionar Asignatura --</option>
          {asignaturas.map(s => (
            <option key={s.id} value={s.id}>{s.nombre}</option>
          ))}
        </select>

        <label>¿A qué aula pertenece?</label>
        <select className="input-field" required value={asignacion.aula} onChange={e => setAsignacion({...asignacion, aula: e.target.value})}>
          <option value="">-- Seleccionar Aula --</option>
          {aulas.map(a => (
            <option key={a.id} value={a.id}>{a.grado_nombre} - "{a.nombre_seccion}"</option>
          ))}
        </select>

        <label>¿Quién lo enseña?</label>
        <select className="input-field" required value={asignacion.profesor} onChange={e => setAsignacion({...asignacion, profesor: e.target.value})}>
          <option value="">-- Seleccionar Profesor --</option>
          {profesores.map(p => (
            <option key={p.id} value={p.id}>{p.nombres} {p.apellidos}</option>
          ))}
        </select>

        <button type="submit" className="btn-primary">Asignar</button>
      </form>
    </div>
  );
};

// ESTILOS EN LINEA SIMPLES
const estiloMenu = (activo) => ({
    padding: '15px',
    cursor: 'pointer',
    background: activo ? 'rgba(255,255,255,0.2)' : 'transparent',
    fontWeight: activo ? 'bold' : 'normal',
    borderRadius: '8px',
    marginBottom: '5px'
});

const estiloForm = {
    background: 'white',
    padding: '30px',
    borderRadius: '10px',
    boxShadow: '0 2px 10px rgba(0,0,0,0.05)',
    maxWidth: '500px'
};

export default GestionDatos;