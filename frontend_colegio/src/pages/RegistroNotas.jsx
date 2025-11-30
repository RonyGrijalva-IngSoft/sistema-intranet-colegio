import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';

const RegistroNotas = () => {
  const { idCurso } = useParams();
  const navigate = useNavigate();

  const [curso, setCurso] = useState(null);
  const [alumnos, setAlumnos] = useState([]);
  const [evaluaciones, setEvaluaciones] = useState([]);
  const [notas, setNotas] = useState({});
  const [loading, setLoading] = useState(true);

  const [periodoActivoId, setPeriodoActivoId] = useState(null);
  // estado para almacenar año del aula
  const [aulaAnio, setAulaAnio] = useState(null);

  useEffect(() => {
    cargarDatosCompletos();
  }, [idCurso]);

  useEffect(() => {
    // Obtener el periodo activo desde el backend
    const fetchPeriodoActivo = async () => {
      try {
        const res = await api.get('periodos/?activo=true');
        const list = Array.isArray(res.data) ? res.data : (res.data && Array.isArray(res.data.results) ? res.data.results : []);
        if (list && list.length > 0) setPeriodoActivoId(list[0].id);
        else setPeriodoActivoId(null);
      } catch (error) {
        console.error('Error obteniendo periodo activo', error);
        setPeriodoActivoId(null);
      }
    };
    fetchPeriodoActivo();
  }, []);

  const cargarDatosCompletos = async () => {
    try {
      setLoading(true);
      const resCurso = await api.get(`cursos-asignados/${idCurso}/`);
      setCurso(resCurso.data);
      // obtener año académico del aula para usarlo al crear evaluaciones
      let aulaAnio = null;
      try {
        if (resCurso.data && resCurso.data.aula) {
          const rAula = await api.get(`aulas/${resCurso.data.aula}/`);
          aulaAnio = rAula.data ? rAula.data.anio_academico : null;
        }
      } catch (e) {
        console.warn('No se pudo obtener detalles del aula', e);
      }
      setAulaAnio(aulaAnio);
      
      const resAlumnos = await api.get(`alumnos/?aula=${resCurso.data.aula}`);
      const alumnosList = Array.isArray(resAlumnos.data) ? resAlumnos.data : (resAlumnos.data && Array.isArray(resAlumnos.data.results) ? resAlumnos.data.results : []);
      setAlumnos(alumnosList);

      // Obtener periodo activo que corresponde al año académico del aula
      let periodoActivoParaAula = null;
      try {
        const resActivos = await api.get('periodos/?activo=true');
        const activos = Array.isArray(resActivos.data) ? resActivos.data : (resActivos.data && Array.isArray(resActivos.data.results) ? resActivos.data.results : []);
        if (aulaAnio) {
          const encontrado = activos.find(p => String(p.anio_academico) === String(aulaAnio) || p.anio_academico == aulaAnio);
          if (encontrado) periodoActivoParaAula = encontrado.id;
        }
        if (!periodoActivoParaAula && activos.length > 0) periodoActivoParaAula = activos[0].id; // fallback global
      } catch (e) {
        console.warn('No se pudo obtener periodo activo para aula', e);
      }

      // Cargar evaluaciones, pero mostrar sólo las del periodo activo para el aula
      const resEvaluaciones = await api.get(`evaluaciones/?curso=${idCurso}`);
      const todasEval = Array.isArray(resEvaluaciones.data) ? resEvaluaciones.data : (resEvaluaciones.data && Array.isArray(resEvaluaciones.data.results) ? resEvaluaciones.data.results : []);
      const evalFiltradas = periodoActivoParaAula ? todasEval.filter(e => {
        // e.periodo puede ser id o objeto dependiendo del serializer
        if (e.periodo === undefined || e.periodo === null) return false;
        if (typeof e.periodo === 'object') return String(e.periodo.id) === String(periodoActivoParaAula);
        return String(e.periodo) === String(periodoActivoParaAula);
      }) : [];
      setEvaluaciones(evalFiltradas);
      // También actualizar periodo activo id local para referencia
      setPeriodoActivoId(periodoActivoParaAula);

      const resNotas = await api.get(`notas/?curso=${idCurso}`);
      const notasList = Array.isArray(resNotas.data) ? resNotas.data : (resNotas.data && Array.isArray(resNotas.data.results) ? resNotas.data.results : []);
      const mapaNotas = {};
      notasList.forEach(nota => {
        mapaNotas[`${nota.alumno}-${nota.evaluacion}`] = {
            id: nota.id,
            valor: nota.valor
        };
      });

      // Ensure every alumno-evaluacion pair has an entry.
      // If a nota is missing (null), initialize it to 0 so the UI shows 0
      // and the save step will create the missing nota with value 0.
      (alumnosList || []).forEach(al => {
        (evalFiltradas || []).forEach(eva => {
          const key = `${al.id}-${eva.id}`;
          if (!mapaNotas[key]) {
            mapaNotas[key] = { id: null, valor: '0' };
          }
        });
      });

      setNotas(mapaNotas);

    } catch (error) {
      console.error("Error cargando datos:", error);
    } finally {
      setLoading(false);
    }
  };

  // estado para almacenar año del aula


  const handleAddColumn = async () => {
    const nombre = prompt("Nombre de la evaluación (Ej: Examen 1):");
    if (!nombre) return;

    try {
      // buscamos el periodo activo para el año académico del aula
      const res = await api.get('periodos/?activo=true');
      const activos = Array.isArray(res.data) ? res.data : (res.data && Array.isArray(res.data.results) ? res.data.results : []);
      let periodoId = null;
      if (aulaAnio) {
        const encontrado = activos.find(p => String(p.anio_academico) === String(aulaAnio) || p.anio_academico == aulaAnio);
        if (encontrado) periodoId = encontrado.id;
      } else if (activos.length > 0) {
        // fallback: usar cualquier periodo activo
        periodoId = activos[0].id;
      }

      if (!periodoId) {
        alert("No hay un periodo activo para el año académico de esta aula. Pide a la Directora que marque un periodo activo para el año correspondiente.");
        return;
      }

      await api.post('evaluaciones/', {
        nombre: nombre,
        asignacion: idCurso,
        periodo: periodoId,
        peso: 1
      });
      cargarDatosCompletos();
    } catch (error) {
      console.error(error);
      alert("Error creando columna. Revisa la consola para más detalles.");
    }
  };

  const handleNotaChange = (alumnoId, evaluacionId, valor) => {
    const clave = `${alumnoId}-${evaluacionId}`;
    // allow clearing the field (empty string) while typing
    if (valor === '' || valor === null) {
      setNotas(prev => ({
        ...prev,
        [clave]: { ...prev[clave], valor: '', modificado: true }
      }));
      return;
    }
    // parse and clamp to [0,20]
    const num = parseFloat(valor);
    if (isNaN(num)) {
      // ignore invalid input
      return;
    }
    let clamped = num;
    if (clamped < 0) clamped = 0;
    if (clamped > 20) clamped = 20;
    setNotas(prev => ({
        ...prev,
        [clave]: { ...prev[clave], valor: String(clamped), modificado: true }
    }));
  };

  const handleGuardar = async () => {
    try {
      // Guardar notas secuencialmente para capturar errores individuales y mensajes de validación
      const failed = [];
      let clamps = 0;
      const keys = Object.keys(notas);
      for (const clave of keys) {
        const notaData = notas[clave];
        if (!(notaData && (notaData.modificado || (!notaData.id && (notaData.valor !== undefined && notaData.valor !== null && notaData.valor !== ''))))) continue;
        const [alumnoId, evaluacionId] = clave.split('-');
        // normalize value
        let valorRaw = notaData.valor;
        if (valorRaw === undefined || valorRaw === null || valorRaw === '') valorRaw = 0;
        let num = Number(valorRaw);
        if (Number.isNaN(num)) num = 0;
        const orig = num;
        if (num < 0) num = 0;
        if (num > 20) num = 20;
        if (num !== orig) clamps += 1;

        const payload = { alumno: alumnoId, evaluacion: evaluacionId, valor: num };

        try {
          if (notaData.id) {
            await api.put(`notas/${notaData.id}/`, payload);
          } else {
            await api.post('notas/', payload);
          }
        } catch (err) {
          // Recoger información útil para debug: status y body si existe
          const info = {
            clave,
            alumno: alumnoId,
            evaluacion: evaluacionId,
            payload,
            status: err?.response?.status || 'network',
            data: err?.response?.data || err.message || String(err)
          };
          console.error('Error guardando nota', info);
          failed.push(info);
        }
      }

      if (failed.length > 0) {
        // Mostrar al usuario un mensaje conciso y log completo en consola
        console.error('Algunos registros fallaron al guardar. Ver detalles en consola:', failed);
        alert(`Error guardando ${failed.length} nota(s). Revisa la consola para más detalles.`);
      } else {
        if (clamps > 0) console.log(`Notas guardadas. ${clamps} valor(es) fueron ajustados para cumplir el rango 0–20.`);
        else console.log('Notas guardadas correctamente');
      }
      await cargarDatosCompletos();

    } catch (error) {
      console.error(error);
      alert("Hubo un error al guardar.");
    }
  };

  const calcularPromedio = (alumnoId) => {
    // Buscar si hay una evaluación tipo "Examen Bimestral" (flexible: contains, case-insensitive)
    const examenEval = evaluaciones.find(e => e.nombre && String(e.nombre).toLowerCase().includes('examen bimestral'));

    // Calcular promedio base IGNORANDO la evaluación de examen (si existe)
    let total = 0;
    let totalPeso = 0;
    evaluaciones.forEach(eva => {
      if (examenEval && eva.id === examenEval.id) return; // omitimos examen
      const clave = `${alumnoId}-${eva.id}`;
      const notaStr = notas[clave]?.valor;
      if (notaStr !== undefined && notaStr !== null && notaStr !== '') {
        const valor = parseFloat(notaStr);
        const peso = eva.peso || 1;
        if (!isNaN(valor)) {
          total += valor * peso;
          totalPeso += peso;
        }
      }
    });

    let promedioBase = null;
    if (totalPeso > 0) promedioBase = total / totalPeso;

    // Si existe examen, mezclarlo con el promedioBase
    if (examenEval) {
      const claveEx = `${alumnoId}-${examenEval.id}`;
      const notaExStr = notas[claveEx]?.valor;
      if (notaExStr !== undefined && notaExStr !== null && notaExStr !== '') {
        const notaEx = parseFloat(notaExStr);
        if (isNaN(notaEx)) return promedioBase;
        if (promedioBase === null) return notaEx;
        return (promedioBase + notaEx) / 2;
      }
    }

    if (promedioBase === null) return null;
    return promedioBase;
  };

  if (loading) return <div style={{padding: '20px'}}>Cargando registro...</div>;

  return (
    <div style={{ padding: '30px', background: '#f9fafb', minHeight: '100vh', fontFamily: 'sans-serif' }}>
      
      <button onClick={() => navigate('/dashboard')} style={{ marginBottom: '20px', border: 'none', background: 'transparent', color: '#666', cursor: 'pointer' }}>
        ← Volver al Dashboard
      </button>

      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
        <div>
          <h1 style={{ margin: '0 0 5px', color: '#111' }}>{curso?.curso_nombre}</h1>
          <span style={{ background: '#dbeafe', color: '#1e40af', padding: '5px 10px', borderRadius: '15px', fontSize: '0.8rem', fontWeight: 'bold' }}>
            {curso?.grado} - {curso?.aula_nombre}
          </span>
        </div>
        
        <div style={{ display: 'flex', gap: '10px' }}>
            <button 
              onClick={handleAddColumn}
              style={{ padding: '10px 20px', background: 'white', border: '1px solid #ddd', borderRadius: '6px', cursor: 'pointer' }}
            >
              + Agregar Columna
            </button>
            <button 
              onClick={handleGuardar}
              className="btn-primary" 
              style={{ width: 'auto' }}
            >
              Guardar Notas
            </button>
        </div>
      </header>

      <div style={{ background: 'white', borderRadius: '8px', boxShadow: '0 2px 5px rgba(0,0,0,0.05)', overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: '600px' }}>
          <thead style={{ background: '#f8fafc', borderBottom: '1px solid #e2e8f0' }}>
            <tr>
              <th style={{ padding: '15px', textAlign: 'left', color: '#64748b' }}>Estudiante</th>
              {evaluaciones.map(eva => (
                <th key={eva.id} style={{ padding: '10px', textAlign: 'center', minWidth: '80px', borderLeft: '1px solid #e2e8f0' }}>
                    <div style={{display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8}}>
                      <div style={{fontSize: '0.85rem', color: '#334155'}}>{eva.nombre}</div>
                      <button onClick={async () => {
                        if (!confirm(`¿Eliminar la evaluación "${eva.nombre}"? Esto borrará también las notas asociadas.`)) return;
                        try {
                          await api.delete(`evaluaciones/${eva.id}/`);
                          console.log('Evaluación eliminada');
                          cargarDatosCompletos();
                        } catch (err) {
                          console.error('Error eliminando evaluación', err);
                          alert('No se pudo eliminar la evaluación. Revisa la consola.');
                        }
                      }}
                      style={{ background: 'transparent', border: 'none', color: '#ef4444', cursor: 'pointer', opacity: 0.55, transition: 'opacity 120ms ease' }}
                      onMouseEnter={(e) => e.currentTarget.style.opacity = 1}
                      onMouseLeave={(e) => e.currentTarget.style.opacity = 0.55}
                      title="Eliminar evaluación">x</button>
                    </div>
                </th>
              ))}
              <th style={{ padding: '10px', textAlign: 'center', minWidth: '90px', borderLeft: '1px solid #e2e8f0' }}>
                <div style={{fontSize: '0.85rem', color: '#334155'}}>Promedio</div>
              </th>
            </tr>
          </thead>
          <tbody>
            {alumnos.map((alumno) => (
              <tr key={alumno.id} style={{ borderBottom: '1px solid #f1f5f9' }}>
                <td style={{ padding: '15px' }}>
                  <div style={{ fontWeight: '500', color: '#0f172a' }}>{alumno.apellidos}, {alumno.nombres}</div>
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>{alumno.dni}</div>
                </td>
                {evaluaciones.map(eva => {
                    const clave = `${alumno.id}-${eva.id}`;
                    const nota = notas[clave]?.valor || '';
                    return (
                        <td key={eva.id} style={{ padding: '10px', textAlign: 'center', borderLeft: '1px solid #f1f5f9' }}>
                            <input 
                                type="number" 
                                min="0" max="20"
                                value={nota}
                                onChange={(e) => handleNotaChange(alumno.id, eva.id, e.target.value)}
                                style={{ 
                                    width: '50px', textAlign: 'center', padding: '8px', border: '1px solid #cbd5e1', borderRadius: '4px', fontWeight: 'bold',
                                    color: nota !== '' && nota < 11 ? '#ef4444' : '#0f172a'
                                }}
                            />
                        </td>
                    );
                })}
                  <td style={{ padding: '10px', textAlign: 'center', borderLeft: '1px solid #f1f5f9', fontWeight: 'bold' }}>
                      {(() => {
                        const prom = calcularPromedio(alumno.id);
                        if (prom === null) return '-';
                        const formatted = Number(prom).toFixed(2);
                        const isBajo = Number(formatted) < 11;
                        return (
                          <span style={{ color: isBajo ? '#ef4444' : '#0f172a' }}>{formatted}</span>
                        );
                      })()}
                  </td>
              </tr>
            ))}
          </tbody>
        </table>
        {alumnos.length === 0 && <p style={{padding: 20, textAlign: 'center'}}>No hay alumnos en esta aula.</p>}
      </div>
    </div>
  );
};

export default RegistroNotas;