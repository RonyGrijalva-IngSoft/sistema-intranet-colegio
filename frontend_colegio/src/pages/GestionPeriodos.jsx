import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { useNavigate } from 'react-router-dom';

const GestionPeriodos = () => {
  const [anios, setAnios] = useState([]);
  const [selectedAnio, setSelectedAnio] = useState(null);
  const [periodos, setPeriodos] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetch = async () => {
      try {
        const normalizeList = (data) => {
          if (!data) return [];
          if (Array.isArray(data)) return data;
          if (data && Array.isArray(data.results)) return data.results;
          return [];
        };

        const resAnios = await api.get('anios/');
        setAnios(normalizeList(resAnios.data));
        const resPeriodos = await api.get('periodos/');
        setPeriodos(normalizeList(resPeriodos.data));
      } catch (err) {
        console.error('Error cargando periodos/anios', err);
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, []);

  const periodosParaAnio = () => {
    if (!selectedAnio) return [];
    return periodos.filter(p => {
      // `p.anio_academico` puede ser un id (number) o un objeto { id, nombre }
      const pAnio = (p && typeof p.anio_academico === 'object' && p.anio_academico !== null) ? p.anio_academico.id : p.anio_academico;
      const sId = selectedAnio && (selectedAnio.id || selectedAnio);
      return String(pAnio) === String(sId);
    });
  };

  const marcarActivo = async (p) => {
    if (!confirm(`Marcar periodo "${p.nombre}" como activo para el año ${selectedAnio.nombre || selectedAnio.id}?`)) return;
    try {
      // Use server-side atomic action to set active period (avoids race conditions)
      const postRes = await api.post(`periodos/${p.id}/set_active/`);
      console.log('set_active response:', postRes);
      if (!postRes || (postRes.status && postRes.status >= 400)) {
        const detail = postRes?.data || postRes?.statusText || 'Error desconocido';
        console.error('Error en set_active:', detail);
        alert('No fue posible activar el periodo: ' + JSON.stringify(detail));
        return;
      }

      // Refrescar la lista desde el servidor
      const res = await api.get('periodos/');
      console.log('GET /periodos response:', res);
      const normalizeList = (data) => {
        if (!data) return [];
        if (Array.isArray(data)) return data;
        if (data && Array.isArray(data.results)) return data.results;
        return [];
      };
      const freshPeriodos = normalizeList(res.data);
      setPeriodos(freshPeriodos);
      // Force selectedAnio to reference the object from `anios` state (helps the filter and re-render)
      setSelectedAnio(prev => {
        if (!prev) return prev;
        const prevId = prev.id || prev;
        const found = anios.find(a => String(a.id) === String(prevId));
        return found || prev;
      });
      console.log('Periodos refrescados', freshPeriodos);
      console.log('Periodo actualizado correctamente');
    } catch (err) {
      console.error(err);
      alert('Error actualizando periodos');
    }
  };

  if (loading) return <div style={{ padding: 20 }}>Cargando periodos...</div>;

  return (
    <div style={{ padding: 30, fontFamily: 'inherit' }}>
      <button
        onClick={() => navigate('/admin')}
        style={{
          marginBottom: 20,
          background: '#d1fae5',
          border: 'none',
          padding: '8px 12px',
          borderRadius: 8,
          cursor: 'pointer',
          fontFamily: 'inherit',
          fontWeight: 600,
          color: '#065f46'
        }}
      >&larr; Volver</button>
      <h1>Gestión de Períodos</h1>
      <p style={{ color: '#6b7280' }}>Seleccione el año académico y marque cuál periodo está activo.</p>

      <div style={{ marginTop: 16 }}>
        <label style={{ marginRight: 8 }}>Año académico:</label>
        <select
          style={{
            background: '#989a9dd4',
            border: 'none',
            padding: '8px 12px',
            borderRadius: 999,
            fontFamily: 'inherit',
            fontWeight: 600,
            color: '#0f172a',
            outline: 'none',
            boxShadow: 'none',
            WebkitAppearance: 'none',
            MozAppearance: 'none',
            appearance: 'none'
          }}
          value={selectedAnio ? selectedAnio.id : ''}
          onChange={(e) => {
          const id = e.target.value;
          const found = anios.find(a => String(a.id) === String(id));
          setSelectedAnio(found || null);
        }}>
          <option value="">-- Seleccionar año --</option>
          {anios.map(a => (
            <option key={a.id} value={a.id}>{(a.anio && String(a.anio).length >= 3) ? a.anio : (a.nombre ? a.nombre : `Año ${a.id}`)}</option>
          ))}
        </select>
      </div>

      <div style={{ marginTop: 20 }}>
          {selectedAnio ? (
          <div>
            <h3>Períodos para {selectedAnio && selectedAnio.anio ? selectedAnio.anio : (selectedAnio && selectedAnio.nombre ? selectedAnio.nombre : (selectedAnio && selectedAnio.id ? `Año ${selectedAnio.id}` : ''))}</h3>
            <ul style={{ listStyle: 'none', padding: 0 }}>
              {periodosParaAnio().map(p => (
                <li key={p.id} style={{ padding: 10, border: '1px solid #e5e7eb', borderRadius: 8, marginBottom: 8, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontWeight: 600 }}>{p.nombre}</div>
                    <div style={{ fontSize: '0.85rem', color: '#6b7280' }}>Activo: {p.activo ? 'Sí' : 'No'}</div>
                  </div>
                  <div>
                    {!p.activo && (
                      <button
                        onClick={() => marcarActivo(p)}
                        style={{
                          padding: '8px 14px',
                          background: 'transparent',
                          border: 'none',
                          color: '#0f172a',
                          cursor: 'pointer',
                          borderRadius: 999,
                          fontFamily: 'inherit',
                          fontWeight: 600
                        }}
                        onMouseOver={(e) => e.currentTarget.style.background = 'rgba(15,98,54,0.06)'}
                        onMouseOut={(e) => e.currentTarget.style.background = 'transparent'
                        }
                      >
                        Marcar activo
                      </button>
                    )}
                    {p.activo && <span style={{ color: '#059669', fontWeight: '600' }}>Activo</span>}
                  </div>
                </li>
              ))}
            </ul>
          </div>
        ) : (
          <div style={{ color: '#9ca3af', marginTop: 12 }}>Selecciona un año académico para ver sus periodos.</div>
        )}
      </div>
    </div>
  );
};

export default GestionPeriodos;
