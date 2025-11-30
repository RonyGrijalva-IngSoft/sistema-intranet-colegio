import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { useNavigate } from 'react-router-dom';

const AulasList = () => {
  const [aulas, setAulas] = useState([]);
  const [estudiantesPorAula, setEstudiantesPorAula] = useState({});
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

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
      <button onClick={() => navigate('/admin')} style={{ marginBottom: 20 }}>&larr; Volver</button>
      <h1 style={{ marginBottom: 10 }}>Aulas y Estudiantes</h1>
      <p style={{ color: '#6b7280', marginBottom: 20 }}>Listado de todas las aulas con sus estudiantes y el tutor asignado.</p>

      <div style={{ display: 'grid', gap: '16px' }}>
        {aulas.map(aula => (
          <div key={aula.id} style={{ border: '1px solid #e5e7eb', borderRadius: 8, padding: 16, background: 'white' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ fontWeight: 'bold', color: '#0f172a' }}>{aula.grado_nombre} - Sección "{aula.nombre_seccion}"</div>
                <div style={{ fontSize: '0.9rem', color: '#6b7280' }}>Año: {aula.anio_academico}</div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontWeight: '600' }}>Tutor</div>
                <div style={{ color: '#374151' }}>{aula.tutor_nombre || 'Sin asignar'}</div>
              </div>
            </div>

            <div style={{ marginTop: 12 }}>
              <div style={{ fontWeight: '600', marginBottom: 8 }}>Estudiantes ({(estudiantesPorAula[aula.id] || []).length})</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                {(estudiantesPorAula[aula.id] || []).length === 0 && <div style={{ color: '#9ca3af' }}>No hay estudiantes en esta aula.</div>}
                {(estudiantesPorAula[aula.id] || []).map(est => (
                  <div key={est.id} style={{ padding: '6px 10px', background: '#f8fafc', borderRadius: 6 }}>{est.nombres} {est.apellidos} ({est.dni})</div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AulasList;
