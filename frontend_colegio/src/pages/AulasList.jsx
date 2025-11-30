import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { useNavigate } from 'react-router-dom';

const AulasList = () => {
  const [aulas, setAulas] = useState([]);
  const [estudiantesPorAula, setEstudiantesPorAula] = useState({});
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const formatYear = (val) => {
    if (val === undefined || val === null) return '';
    // If already a 4-digit year, return as-is; otherwise return the raw value
    const n = Number(val);
    if (Number.isInteger(n) && n >= 1900 && n <= 3000) return String(n);
    return String(val);
  };

  useEffect(() => {
    const fetchAulas = async () => {
      try {
        const res = await api.get('aulas/');
        const aulasList = Array.isArray(res.data) ? res.data : (res.data && Array.isArray(res.data.results) ? res.data.results : []);
        setAulas(aulasList);
        // Para cada aula, pedimos sus alumnos
        const map = {};
        await Promise.all(aulasList.map(async (aula) => {
          try {
            const r = await api.get(`alumnos/?aula=${aula.id}`);
            const alumnos = Array.isArray(r.data) ? r.data : (r.data && Array.isArray(r.data.results) ? r.data.results : []);
            map[aula.id] = alumnos;
          } catch (err) {
            map[aula.id] = [];
          }
        }));
        setEstudiantesPorAula(map);
      } catch (error) {
        console.error('Error cargando aulas', error);
      } finally {
        setLoading(false);
      }
    };
    fetchAulas();
  }, []);

  if (loading) return <div style={{padding:20}}>Cargando aulas...</div>;

  return (
    <div style={{ padding: 30, fontFamily: 'sans-serif' }}>
      <button onClick={() => navigate('/admin')} style={{           
        marginBottom: 20,
          background: '#d1fae5',
          border: 'none',
          padding: '8px 12px',
          borderRadius: 999,
          cursor: 'pointer',
          fontFamily: 'inherit',
          fontWeight: 600,
          color: '#065f46'}}>&larr; Volver</button>
      <h1 style={{ marginBottom: 10 }}>Aulas y Estudiantes</h1>
      <p style={{ color: '#6b7280', marginBottom: 20 }}>Listado de todas las aulas con sus estudiantes y el tutor asignado.</p>

      <div style={{ display: 'grid', gap: '16px', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))' }}>
        {aulas.map(aula => (
          <div key={aula.id} style={{ border: '2px solid #f97316', borderRadius: 10, padding: 16, background: 'white', boxShadow: '0 1px 2px rgba(0,0,0,0.04)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <div style={{ fontWeight: '700', color: '#0f172a', marginBottom: 6 }}>{aula.grado_nombre} - Sección "{aula.nombre_seccion}"</div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontWeight: 700, color: '#0f172a' }}>Tutor</div>
                <div style={{ color: '#374151' }}>{aula.tutor_nombre || 'Sin asignar'}</div>
              </div>
            </div>

            <div style={{ marginTop: 12 }}>
              <div style={{ fontWeight: 600, marginBottom: 8 }}>Estudiantes ({(estudiantesPorAula[aula.id] || []).length})</div>
              {(estudiantesPorAula[aula.id] || []).length === 0 ? (
                <div style={{ color: '#9ca3af' }}>No hay estudiantes en esta aula.</div>
              ) : (
                <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                  {(estudiantesPorAula[aula.id] || []).map(est => (
                    <li key={est.id} style={{ padding: '8px 10px', background: '#f8fafc', borderRadius: 6, marginBottom: 8 }}>{(est.nombres || '') + (est.apellidos ? ' ' + est.apellidos : '')}</li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AulasList;
