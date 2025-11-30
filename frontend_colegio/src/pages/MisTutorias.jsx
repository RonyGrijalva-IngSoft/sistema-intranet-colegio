import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { useNavigate } from 'react-router-dom';

const MisTutorias = () => {
  const [aulas, setAulas] = useState([]);
  const [estudiantesPorAula, setEstudiantesPorAula] = useState({});
  const [periodoActivo, setPeriodoActivo] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetch = async () => {
      try {
        // obtener info usuario
        const ui = await api.get('user-info/');
        const profesorId = ui.data.profesor_id;
        if (!profesorId) {
          setAulas([]);
          setLoading(false);
          return;
        }

        // cargar aulas donde es tutor
        const res = await api.get('aulas/');
        const aulasList = Array.isArray(res.data) ? res.data : (res.data && Array.isArray(res.data.results) ? res.data.results : []);
        const tutorAulas = aulasList.filter(a => a.tutor === profesorId);
        setAulas(tutorAulas);

        // periodo activo
        const p = await api.get('periodos/?activo=true');
        const periodosList = Array.isArray(p.data) ? p.data : (p.data && Array.isArray(p.data.results) ? p.data.results : []);
        const periodo = (periodosList && periodosList.length > 0) ? periodosList[0] : null;
        setPeriodoActivo(periodo);

        const map = {};
        await Promise.all(tutorAulas.map(async (aula) => {
            try {
            const r = await api.get(`alumnos/?aula=${aula.id}`);
            const alumnos = Array.isArray(r.data) ? r.data : (r.data && Array.isArray(r.data.results) ? r.data.results : []);
            // If we have an active period, fetch each student's libreta for that period to get promedio_ponderado
            if (periodo) {
              await Promise.all(alumnos.map(async (al) => {
                try {
                  const lr = await api.get(`libretas/?alumno=${al.id}&periodo=${periodo.id}`);
                  const lrList = Array.isArray(lr.data) ? lr.data : (lr.data && Array.isArray(lr.data.results) ? lr.data.results : []);
                  if (lrList && lrList.length > 0) {
                    al.promedio_ponderado = lrList[0].promedio_ponderado;
                  } else {
                    al.promedio_ponderado = null;
                  }
                } catch (e) {
                  al.promedio_ponderado = null;
                }
              }));
            }
            map[aula.id] = alumnos;
          } catch (err) {
            map[aula.id] = [];
          }
        }));
        setEstudiantesPorAula(map);
      } catch (error) {
        console.error('Error cargando tutorias', error);
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, []);

  // Helper to parse promedio values: accept comma or dot decimals, return Number or null
  const parsePromedio = (v) => {
    if (v === undefined || v === null) return null;
    const s = String(v).replace(',', '.').trim();
    const n = Number(s);
    return Number.isFinite(n) ? n : null;
  };

  const handleAprobar = async (libretaId) => {
    if (!confirm('¿Aprobar esta libreta y enviar a Dirección?')) return;
    try {
      await api.post(`libretas/${libretaId}/aprobar_por_tutor/`);
      console.log('Libreta aprobada y enviada a Dirección');
      // refrescar
      window.location.reload();
    } catch (err) {
      console.error(err);
      alert('Error aprobando libreta');
    }
  };

  // Estado para modal de ver libreta
  const [modalOpen, setModalOpen] = useState(false);
  const [modalStudent, setModalStudent] = useState(null);
  const [modalAula, setModalAula] = useState(null);
  const [modalTable, setModalTable] = useState(null);
  const [modalLibreta, setModalLibreta] = useState(null);
  const [modalPuesto, setModalPuesto] = useState(null);
  const [tutorComment, setTutorComment] = useState('');

  const handleVerLibreta = async (alumno, aula) => {
    // Abrir modal y construir la tabla
    setModalOpen(true);
    setModalStudent(alumno);
    setModalAula(aula);
    setModalTable(null);
    setModalLibreta(null);
    setModalPuesto(null);
    setTutorComment('');

    try {
      // 1) Obtener cursos asignados (traemos todos y filtramos localmente por aula para mayor robustez)
      const resCursos = await api.get('cursos-asignados/');
      const cursosList = Array.isArray(resCursos.data) ? resCursos.data : (resCursos.data && Array.isArray(resCursos.data.results) ? resCursos.data.results : []);
      // Filtrar teniendo en cuenta distintas formas de serialización (aula id directo o objeto aula)
      const cursos = cursosList.filter(c => {
        try {
          if (c.aula === aula.id) return true;
          if (c.aula_id === aula.id) return true;
          if (c.aula && (c.aula.id === aula.id || String(c.aula) === String(aula.id))) return true;
        } catch (e) {
          return false;
        }
        return false;
      });

      // 2) Obtener todos los periodos del sistema y filtrar por año del aula
      const resPeriodos = await api.get('periodos/');
      const periodosAll = Array.isArray(resPeriodos.data) ? resPeriodos.data : (resPeriodos.data && Array.isArray(resPeriodos.data.results) ? resPeriodos.data.results : []);
      const periodosAula = periodosAll.filter(p => String(p.anio_academico) === String(aula.anio_academico) || p.anio_academico == aula.anio_academico);
      // Ordenamos por id (o por nombre) y tomamos hasta 4 bimestres
      periodosAula.sort((a,b) => a.id - b.id);
      const periodos = periodosAula.slice(0, 4);

      // 3) Para optimizar: traer todas las libretas del alumno en UNA sola petición
      const allLibretasResp = await api.get(`libretas/?alumno=${alumno.id}`);
      const allLibretas = Array.isArray(allLibretasResp.data) ? allLibretasResp.data : (allLibretasResp.data && Array.isArray(allLibretasResp.data.results) ? allLibretasResp.data.results : []);
      // Mapear por periodo -> libreta (si hay varias, tomamos la primera)
      const libretasByPeriodo = {};
      for (const lb of allLibretas) {
        try {
          const pid = lb.periodo && (lb.periodo.id || lb.periodo) ? (lb.periodo.id || lb.periodo) : null;
          if (pid != null && !(String(pid) in libretasByPeriodo)) libretasByPeriodo[String(pid)] = lb;
        } catch (e) {
          continue;
        }
      }

      // Construir la tabla usando las libretas ya cargadas
      const table = [];
      for (const curso of cursos) {
        const row = { curso: curso, valores: [], promedio: null };
        const valores = [];
        for (const per of periodos) {
          let promedio = null;
          const libreta = libretasByPeriodo[String(per.id)];
          if (libreta) {
            const detalles = libreta.detalles || {};
            const detalleAsign = detalles[String(curso.id)];
            if (detalleAsign && detalleAsign.promedio != null) promedio = parsePromedio(detalleAsign.promedio);
            if (periodoActivo && String(per.id) === String(periodoActivo.id)) {
              setModalLibreta(libreta);
              setTutorComment(libreta.observacion_tutor || '');
            }
          }
          valores.push(promedio);
        }

        const nums = valores.filter(v => v !== null && v !== undefined && Number.isFinite(v));
        const prom = nums.length ? (nums.reduce((a,b)=>a+b,0)/nums.length) : null;
        row.valores = valores;
        row.promedio = prom;
        table.push(row);
      }

      setModalTable({ periodos, table });
      // calcular puesto dentro del aula para el periodo activo
          try {
            if (periodoActivo) {
              const resP = await api.get(`libretas/?periodo=${periodoActivo.id}&aula=${aula.id}`);
              const lista = Array.isArray(resP.data) ? resP.data : (resP.data && Array.isArray(resP.data.results) ? resP.data.results : []);
              lista.sort((a, b) => {
                const aa = parsePromedio(a.promedio_ponderado) ?? Number.NEGATIVE_INFINITY;
                const bb = parsePromedio(b.promedio_ponderado) ?? Number.NEGATIVE_INFINITY;
                return bb - aa;
              });
              const idx = lista.findIndex(lb => String(lb.alumno) === String(alumno.id));
              if (idx >= 0) setModalPuesto({ index: idx + 1, total: lista.length });
            }
          } catch (e) {
            // ignore
          }
    } catch (err) {
      console.error('Error construyendo libreta', err);
      setModalTable({ periodos: [], table: [] });
    }
  };

  if (loading) return <div style={{padding:20}}>Cargando tutorías...</div>;

  const pageFont = "Inter, system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial";

  return (
    <>
    <div style={{ padding: 30, fontFamily: pageFont }}>
      <button onClick={() => navigate('/dashboard')} style={{ marginBottom: 20, padding: '8px 12px', fontFamily: 'sans-serif', borderRadius: 999, cursor: 'pointer' }}>&larr; Volver</button>
      <h1 style={{ marginBottom: 10 }}>Mis Tutorías</h1>
      <p style={{ color: '#6b7280', marginBottom: 20 }}>Vea a sus estudiantes por aula y las libretas de periodo activo.</p>

      {aulas.length === 0 && <div>No estás asignado como tutor a ninguna aula.</div>}

      <div style={{ display: 'grid', gap: 16 }}>
        {aulas.map(aula => (
          <div key={aula.id} style={{ border: '1px solid #e5e7eb', borderRadius: 10, padding: 16, background: 'white' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ fontWeight: 'bold' }}>{aula.grado_nombre} - Sección "{aula.nombre_seccion}"</div>
                <div style={{ fontSize: '0.9rem', color: '#6b7280' }}>Año: {aula.anio_academico}</div>
              </div>
            </div>

            <div style={{ marginTop: 12 }}>
              <div style={{ fontWeight: '600', marginBottom: 8 }}>Estudiantes ({(estudiantesPorAula[aula.id] || []).length})</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                {(estudiantesPorAula[aula.id] || []).slice().sort((a,b) => {
                  // Sort by promedio_ponderado descending (nulls at the end), fallback to id ascending
                  const pa = parsePromedio(a.promedio_ponderado);
                  const pb = parsePromedio(b.promedio_ponderado);
                  if (pa === null && pb === null) return Number(a.id) - Number(b.id);
                  if (pa === null) return 1;
                  if (pb === null) return -1;
                  if (pb === pa) return Number(a.id) - Number(b.id);
                  return pb - pa;
                }).map(est => (
                  <div key={est.id} style={{ padding: 12, borderRadius: 8, background: '#ffffff', display: 'flex', justifyContent: 'space-between', alignItems: 'center', border: '1px solid #fb923c', width: '48%', alignSelf: 'center' }}>
                    <div>
                      <div style={{ fontWeight: 600, fontFamily: pageFont }}>{est.apellidos}, {est.nombres}</div>
                    </div>
                    <div style={{ display: 'flex', gap: 8 }}>
                      <button onClick={() => handleVerLibreta(est, aula)} style={{ padding: '8px 12px', borderRadius: 999, background: '#e6f4f0', color: '#0f172a', cursor: 'pointer' }}>Ver Libreta</button>
                      <LibretaAction alumnoId={est.id} periodoId={periodoActivo ? periodoActivo.id : null} onAprobar={handleAprobar} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
    <LibretaModal open={modalOpen} onClose={() => setModalOpen(false)} student={modalStudent} aula={modalAula} data={modalTable} libreta={modalLibreta} puesto={modalPuesto} comentario={tutorComment} onChangeComentario={setTutorComment} />
    </>
  );
};

// Render modal from inside MisTutorias by exposing modal state
// We'll attach the modal component at module level but call it from inside the component's JSX via state.

// Modal para mostrar la libreta con el mismo formato que la Directora
const LibretaModal = ({ open, onClose, student, aula, data, libreta, puesto, comentario, onChangeComentario }) => {
  if (!open) return null;
  const periodos = (data && data.periodos) || [];
  const rows = (data && data.table) || [];

  const guardarComentario = async () => {
    if (!libreta) return alert('No hay libreta para guardar comentario');
    try {
      await api.patch(`libretas/${libreta.id}/`, { observacion_tutor: comentario });
      console.log('Comentario guardado');
    } catch (e) {
      console.error(e);
      alert('Error guardando comentario');
    }
  };

  const calcularPromedioFinalBimestre = () => {
    if (!rows.length) return '-';
    // Suma de promedios finales por curso dividido entre número de cursos (cursos sin nota cuentan como 0)
    const suma = rows.reduce((acc, r) => {
      const nums = (r.valores || []).filter(v => v !== null && v !== undefined).map(Number);
      const rowAvg = nums.length ? (nums.reduce((a, b) => a + b, 0) / nums.length) : 0;
      return acc + rowAvg;
    }, 0);
    const total = rows.length;
    const resultado = suma / total;
    return Number.isFinite(resultado) ? resultado.toFixed(2) : '-';
  };

  return (
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.4)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 50 }}>
      <div style={{ width: '90%', maxWidth: 1000, background: 'white', borderRadius: 8, padding: 20, maxHeight: '80vh', overflow: 'auto' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2>Libreta — {student.apellidos}, {student.nombres} — {periodos[periodos.length - 1]?.nombre || ''}</h2>
          <div>
            <button onClick={onClose} style={{ padding: '6px 10px', fontFamily: 'sans-serif', borderRadius: 999, cursor: 'pointer' }}>Cerrar</button>
          </div>
        </div>

        {!data && <div>Cargando...</div>}
        {data && (
          <>
            <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: 12 }}>
              <thead>
                <tr>
                  <th style={{ border: '1px solid #e5e7eb', padding: 8 }}>Curso</th>
                  {periodos.map(p => (
                    <th key={p.id} style={{ border: '1px solid #e5e7eb', padding: 8, textAlign: 'center' }}>{p.nombre}</th>
                  ))}
                  <th style={{ border: '1px solid #e5e7eb', padding: 8, textAlign: 'center' }}>Promedio Final</th>
                </tr>
              </thead>
              <tbody>
                {rows.map(row => (
                  <tr key={row.curso.id}>
                    <td style={{ border: '1px solid #e5e7eb', padding: 8 }}>{(row.curso.asignatura?.nombre || row.curso.curso_nombre || row.curso.asignatura_nombre || row.curso.nombre || 'Sin nombre')}</td>
                    {(row.valores || []).map((v, i) => (
                      <td key={i} style={{ border: '1px solid #e5e7eb', padding: 8, textAlign: 'center' }}>{v !== null && v !== undefined ? Number(v).toFixed(2) : '-'}</td>
                    ))}
                    <td style={{ border: '1px solid #e5e7eb', padding: 8, textAlign: 'center' }}>{row.promedio !== null && row.promedio !== undefined ? Number(row.promedio).toFixed(2) : '0.00'}</td>
                  </tr>
                ))}
              </tbody>
              <tfoot>
                <tr>
                  <td style={{ border: '1px solid #e5e7eb', padding: 8, fontWeight: 700 }} colSpan={periodos.length + 1}>Promedio Final del Bimestre</td>
                  <td style={{ border: '1px solid #e5e7eb', padding: 8, textAlign: 'center', fontWeight: 700 }}>{calcularPromedioFinalBimestre()}</td>
                </tr>
              </tfoot>
            </table>

            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 12 }}>
              <div style={{ width: '60%' }}>
                {/* Comentario del tutor: solo editable si existe libreta (y si el usuario es tutor, controlado desde parent) */}
                <label style={{ fontWeight: 600 }}>Comentario del Tutor</label>
                <textarea value={comentario || ''} onChange={e => onChangeComentario(e.target.value)} style={{ width: '100%', minHeight: 80, marginTop: 6, padding: 8 }} />
                <div style={{ marginTop: 8 }}>
                  <button onClick={guardarComentario} style={{ padding: '8px 12px', fontFamily: 'sans-serif', borderRadius: 999, cursor: 'pointer' }}>Guardar comentario</button>
                </div>
              </div>

              <div style={{ width: 220, textAlign: 'right' }}>
                {puesto ? (
                  <div style={{ border: '1px solid #e5e7eb', padding: 10, borderRadius: 6 }}>
                    <div style={{ fontSize: '0.85rem', color: '#6b7280' }}>Puesto</div>
                    <div style={{ fontSize: '1.6rem', fontWeight: 'bold' }}>{puesto.index} / {puesto.total}</div>
                  </div>
                ) : (
                  <div style={{ color: '#9ca3af' }}>Puesto: -</div>
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

  const LibretaRow = ({ alumnoId, periodoId }) => {
  const [libreta, setLibreta] = useState(null);

  useEffect(() => {
    const fetch = async () => {
      try {
        const res = await api.get(`libretas/?alumno=${alumnoId}&periodo=${periodoId}`);
        if (res.data && res.data.length > 0) setLibreta(res.data[0]);
      } catch (err) {
        console.error(err);
      }
    };
    if (periodoId) fetch();
  }, [alumnoId, periodoId]);

  if (!libreta) return <span style={{ color: '#9ca3af' }}>Sin libreta para este periodo</span>;

  const displayProm = (v) => {
    if (v === undefined || v === null) return '-';
    const s = String(v).replace(',', '.').trim();
    const n = Number(s);
    return Number.isFinite(n) ? n.toFixed(2) : '-';
  };

  return (
    <div>
      <div>Estado: <strong>{libreta.estado}</strong></div>
      <div>Promedio: <strong>{displayProm(libreta.promedio_ponderado)}</strong></div>
    </div>
  );
};

const LibretaAction = ({ alumnoId, periodoId, onAprobar }) => {
  const [libreta, setLibreta] = useState(null);

  useEffect(() => {
    const fetch = async () => {
      try {
        // Si hay periodoId, preferimos esa consulta.
        let res = null;
        if (periodoId) {
          res = await api.get(`libretas/?alumno=${alumnoId}&periodo=${periodoId}`);
        }
        // Si no obtuvimos libreta por periodo, traemos todas las libretas del alumno
        if (!res || !(Array.isArray(res.data) ? res.data.length > 0 : (res.data && Array.isArray(res.data.results) ? res.data.results.length > 0 : false))) {
          res = await api.get(`libretas/?alumno=${alumnoId}`);
        }

        const list = Array.isArray(res.data) ? res.data : (res.data && Array.isArray(res.data.results) ? res.data.results : []);
        if (!list || list.length === 0) {
          setLibreta(null);
          return;
        }

        // Preferir una libreta del periodo activo (si se consultó), o una en REVISION_TUTOR
        let chosen = null;
        if (periodoId) chosen = list.find(l => String(l.periodo) === String(periodoId) || (l.periodo && l.periodo.id && String(l.periodo.id) === String(periodoId)));
        if (!chosen) chosen = list.find(l => l.estado === 'REVISION_TUTOR');
        if (!chosen) chosen = list[0];
        setLibreta(chosen);
      } catch (err) {
        console.error(err);
        setLibreta(null);
      }
    };
    fetch();
  }, [alumnoId, periodoId]);

  if (!libreta) return null;

  if (libreta.estado === 'REVISION_TUTOR') {
    return (
      <button onClick={() => onAprobar(libreta.id)} style={{ padding: '8px 12px', borderRadius: 999, background: '#10b981', color: 'white', border: 'none', cursor: 'pointer' }}>Aprobar Libreta</button>
    );
  }

  return null;
};

export default MisTutorias;
