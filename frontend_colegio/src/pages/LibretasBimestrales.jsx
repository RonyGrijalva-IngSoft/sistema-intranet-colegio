import React, { useEffect, useState, useRef } from 'react';
import api from '../services/api';
import { useNavigate } from 'react-router-dom';
import html2canvas from 'html2canvas';

const LibretasBimestrales = () => {
  const [periodos, setPeriodos] = useState([]);
  const [selectedPeriodo, setSelectedPeriodo] = useState(null);
  const [libretas, setLibretas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modal, setModal] = useState({ open: false, libreta: null, details: null });
  const navigate = useNavigate();
  const printRef = useRef(null);

  useEffect(() => {
    const fetch = async () => {
      setLoading(true);
      try {
        const normalizeList = (data) => {
          if (!data) return [];
          if (Array.isArray(data)) return data;
          if (data && Array.isArray(data.results)) return data.results;
          return [];
        };

        const resP = await api.get('periodos/');
        const listaP = normalizeList(resP.data);
        setPeriodos(listaP);
        const resAct = await api.get('periodos/?activo=true');
        const actList = normalizeList(resAct.data);
        if (actList.length > 0) setSelectedPeriodo(actList[0].id);
      } catch (err) {
        console.error('Error cargando periodos', err);
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, []);

  useEffect(() => {
    if (selectedPeriodo) loadLibretas(selectedPeriodo);
    else setLibretas([]);
  }, [selectedPeriodo]);

  const loadLibretas = async (periodoId) => {
    setLoading(true);
    try {
      const res = await api.get(`libretas/?periodo=${periodoId}`);
      const normalizeList = (data) => {
        if (!data) return [];
        if (Array.isArray(data)) return data;
        if (data && Array.isArray(data.results)) return data.results;
        return [];
      };
      setLibretas(normalizeList(res.data));
    } catch (err) {
      console.error('Error cargando libretas', err);
      setLibretas([]);
    } finally {
      setLoading(false);
    }
  };

  const exportPdf = async () => {
    if (!modal.libreta) return;
    // Do not allow export if libreta is under tutor review
    if (modal.libreta.estado === 'REVISION_TUTOR') {
      alert('Esta libreta está en revisión por el tutor y no puede ser exportada aún.');
      return;
    }
    const input = printRef.current;
    if (!input) {
      alert('Contenido no disponible para exportar. Intenta abrir la libreta primero.');
      return;
    }
    try {
      // Import jsPDF dynamically to avoid Vite import-analysis issues with jspdf packaging
      const { jsPDF } = await import('jspdf');
      const canvas = await html2canvas(input, { scale: 2, useCORS: true });
      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF('p', 'pt', 'a4');
      const imgProps = pdf.getImageProperties(imgData);
      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeightPage = pdf.internal.pageSize.getHeight();
      // Add margins (points)
      const margin = 20; // pts
      const imgWidth = imgProps.width;
      const imgHeight = imgProps.height;
      // scale to fit within pdf page minus margins
      const maxWidth = pdfWidth - margin * 2;
      const maxHeight = pdfHeightPage - margin * 2;
      const ratio = Math.min(maxWidth / imgWidth, maxHeight / imgHeight);
      const drawWidth = imgWidth * ratio;
      const drawHeight = imgHeight * ratio;
      const x = margin;
      const y = margin;
      pdf.addImage(imgData, 'PNG', x, y, drawWidth, drawHeight);
      const fileName = `${modal.libreta.alumno_nombre || 'libreta'}.pdf`;
      pdf.save(fileName);
    } catch (e) {
      console.error('Error creando PDF', e);
      alert('No se pudo crear el PDF. Revisa la consola.');
    }
  };

  const handleExportFromList = async (libreta) => {
    if (libreta.estado === 'REVISION_TUTOR') {
      alert('Esta libreta está en revisión por el tutor y no puede ser exportada.');
      return;
    }
    await openLibreta(libreta);
    setTimeout(() => exportPdf(), 600);
  };

  const openLibreta = async (libreta) => {
    setModal({ open: true, libreta, details: null });
    try {
      const normalizeList = (data) => {
        if (!data) return [];
        if (Array.isArray(data)) return data;
        if (data && Array.isArray(data.results)) return data.results;
        return [];
      };

      const resCursos = await api.get(`cursos-asignados/?aula=${libreta.aula}`);
      const cursos = normalizeList(resCursos.data);
      const resPeriodo = await api.get(`periodos/${libreta.periodo}/`);
      const periodoActual = resPeriodo.data;
      const resPeriodosAnio = await api.get(`periodos/?anio_academico=${periodoActual.anio_academico}`);
      let periodosAnio = normalizeList(resPeriodosAnio.data);
      periodosAnio = periodosAnio.sort((a, b) => a.id - b.id).slice(0, 4);

      const resAll = await api.get(`libretas/?alumno=${libreta.alumno}&aula=${libreta.aula}`);
      const todasLibretas = (normalizeList(resAll.data) || []).filter(lb => periodosAnio.find(p => p.id === lb.periodo));
      const libretasByPeriodo = {};
      todasLibretas.forEach(lb => { libretasByPeriodo[lb.periodo] = lb; });
      const periodoIndex = periodosAnio.findIndex(p => p.id === periodoActual.id);

      const table = cursos.map(curso => ({
        asignId: curso.id,
        nombre: courseNameFromCurso(curso),
        bimestres: periodosAnio.map((p, idx) => {
          if (periodoIndex >= 0 && idx > periodoIndex) return null;
          const lb = libretasByPeriodo[p.id];
          if (!lb) return null;
          const det = lb.detalles || {};
          const d = det[String(curso.id)] || det[curso.id] || null;
          return d && (d.promedio !== undefined) ? Number(d.promedio).toFixed(2) : null;
        })
      }));

      let aulaObj = null;
      try {
        const rAula = await api.get(`aulas/${libreta.aula}/`);
        aulaObj = rAula.data;
        // If aulaObj.grado is an id, fetch the Grado object to obtain its 'nivel'
        try {
          const gradoId = (aulaObj && aulaObj.grado && typeof aulaObj.grado !== 'object') ? aulaObj.grado : null;
          if (gradoId) {
            const rGrado = await api.get(`grados/${gradoId}/`);
            // replace numeric grado with the full object to simplify downstream logic
            aulaObj.grado = rGrado.data;
          }
        } catch (e) {
          console.warn('No se pudo obtener info del grado para aula_obj', e);
        }
      } catch (e) { console.warn('No se pudo obtener info del aula', e); }

      let puesto = null;
      try {
        const resPeriodoAula = await api.get(`libretas/?periodo=${periodoActual.id}&aula=${libreta.aula}`);
        const periodoLibretas = normalizeList(resPeriodoAula.data) || [];
        const promedioForLibreta = (lb) => {
          if (lb.promedio_ponderado !== undefined && lb.promedio_ponderado !== null) return Number(lb.promedio_ponderado);
          const det = lb.detalles || {};
          const suma = cursos.reduce((acc, c) => {
            const d = det[String(c.id)] || det[c.id] || null;
            if (d && (d.promedio !== undefined && d.promedio !== null)) return acc + Number(d.promedio);
            return acc;
          }, 0);
          const count = cursos.reduce((acc, c) => {
            const d = det[String(c.id)] || det[c.id] || null;
            return acc + (d && (d.promedio !== undefined && d.promedio !== null) ? 1 : 0);
          }, 0);
          if (count === 0) return 0;
          return suma / count;
        };
        // Build a numeric ranking and compare alumno IDs as strings to avoid type mismatches
        // Parse averages robustly: accept comma or dot decimals, treat non-numeric as very low so they rank last
        const parsePromedio = (v) => {
          if (v === undefined || v === null) return Number.NEGATIVE_INFINITY;
          const s = String(v).replace(',', '.').trim();
          const n = Number(s);
          return Number.isFinite(n) ? n : Number.NEGATIVE_INFINITY;
        };

        const ranking = periodoLibretas
          .map(lb => ({ alumno: String(lb.alumno), promedio: parsePromedio(promedioForLibreta(lb)) }))
          .sort((a, b) => b.promedio - a.promedio);

        const idx = ranking.findIndex(r => r.alumno === String(libreta.alumno));
        if (idx >= 0) puesto = idx + 1;
      } catch (err) { console.warn('No se pudo calcular puesto:', err); }

      setModal({ open: true, libreta: { ...libreta, periodo_obj: periodoActual, periodos_anio: periodosAnio, aula_obj: aulaObj, puesto }, details: { table } });
    } catch (err) {
      console.error('Error construyendo detalles de libreta', err);
      setModal({ open: true, libreta, details: { table: [] } });
    }
  };

  const courseNameFromCurso = (curso) => {
    if (!curso) return 'Sin nombre';
    if (curso.curso_nombre) return curso.curso_nombre;
    if (curso.asignatura && curso.asignatura.nombre) return curso.asignatura.nombre;
    return curso.asignatura_nombre || curso.nombre || `Asignación ${curso.id}`;
  };

  const getNivelFromAula = (aulaObj) => {
    if (!aulaObj) return '';
    // Try several possible shapes and field names
    // 1) direct nivel field
    if (aulaObj.nivel) return (typeof aulaObj.nivel === 'string') ? aulaObj.nivel : (aulaObj.nivel.nombre || '');
    // 2) grado object with nivel
    if (aulaObj.grado && typeof aulaObj.grado === 'object') {
      const g = aulaObj.grado;
      if (g.nivel) return (typeof g.nivel === 'string') ? g.nivel : (g.nivel.nombre || '');
      if (g.nivel_nombre) return g.nivel_nombre;
    }
    // 3) grado_nivel or nivel_nombre flattened fields
    if (aulaObj.grado_nivel) return aulaObj.grado_nivel;
    if (aulaObj.nivel_nombre) return aulaObj.nivel_nombre;
    if (aulaObj.grado && typeof aulaObj.grado === 'string') {
      // sometimes grado is a string with the name; no nivel available
      return '';
    }

    // 4) Try to infer level from grado_nombre if available (e.g., "1er Grado")
    const gradoNombre = aulaObj.grado_nombre || (aulaObj.grado && aulaObj.grado.nombre) || '';
    if (gradoNombre) {
      // extract leading number (1,2,3,..) from strings like '1er Grado' or '7mo Grado'
      const m = gradoNombre.match(/(\d+)/);
      if (m) {
        const num = parseInt(m[1], 10);
        if (!Number.isNaN(num)) {
          // simple mapping: 1-6 -> Primaria, 7+ -> Secundaria
          if (num >= 1 && num <= 6) return 'Primaria';
          return 'Secundaria';
        }
      }
    }

    return '';
  };

  const aprobarPorDireccion = async (libretaId) => {
    if (!confirm('¿Aprobar esta libreta de forma definitiva?')) return;
    try {
      await api.post(`libretas/${libretaId}/aprobar_por_direccion/`);
      console.log('Libreta aprobada por Dirección');
      if (selectedPeriodo) loadLibretas(selectedPeriodo);
      setModal({ open: false, libreta: null, details: null });
    } catch (err) {
      console.error(err);
      alert('Error aprobando la libreta');
    }
  };

  if (loading) return <div style={{ padding: 20 }}>Cargando libretas...</div>;

  return (
    <div style={{ padding: 30, fontFamily: 'sans-serif' }}>
      <button onClick={() => navigate('/admin')} style={{           
        marginBottom: 20,
          background: '#d1fae5',
          border: 'none',
          padding: '8px 12px',
          borderRadius: 8,
          cursor: 'pointer',
          fontFamily: 'inherit',
          fontWeight: 600,
          color: '#065f46'}}>&larr; Volver</button>
      <h1 style={{ marginBottom: 10 }}>Libretas Bimestrales</h1>
      <p style={{ color: '#6b7280', marginBottom: 16 }}>Seleccione un periodo para ver las libretas de ese bimestre.</p>

      <div style={{ marginBottom: 16 }}>
        <select
          style={{
            background: '#c2c4c8ff',
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
          value={selectedPeriodo || ''}
          onChange={(e) => setSelectedPeriodo(e.target.value)}
        >
          <option value="">-- Seleccionar periodo --</option>
          {periodos.map(p => (
            <option key={p.id} value={p.id}>{p.nombre}{p.activo ? ' - ACTIVO' : ''}</option>
          ))}
        </select>
      </div>

      <div style={{ display: 'grid', gap: 12 }}>
        {libretas.length === 0 && <div>No hay libretas para este periodo.</div>}
        {libretas.map(l => (
          <div key={l.id} style={{ border: '1px solid #e5e7eb', padding: 12, borderRadius: 8, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <div style={{ fontWeight: 600 }}>{l.alumno_nombre} — {l.grado_nombre || l.aula_nombre}</div>
              <div style={{ fontSize: '0.9rem', color: '#6b7280' }}>Estado: {l.estado}</div>
            </div>
            <div style={{ display: 'flex', gap: 8 }}>
              <button onClick={() => openLibreta(l)} style={{                    padding: '6px 10px',
                    background: '#d7dae0ff',
                    color: '#0f172a',
                    border: 'none',
                    borderRadius: 999,
                    fontFamily: 'inherit',
                    fontWeight: 600,
                    cursor: 'pointer'}}>Ver Libreta</button>
              {l.estado === 'ENVIADO_DIRECCION' && (
                <button
                  onClick={() => handleExportFromList(l)}
                  style={{
                    padding: '8px 12px',
                    background: '#059669',
                    color: 'white',
                    border: 'none',
                    borderRadius: 999,
                    fontFamily: 'inherit',
                    fontWeight: 600,
                    cursor: 'pointer'
                  }}
                >Exportar Libreta</button>
              )}
            </div>
          </div>
        ))}
      </div>

      {modal.open && modal.libreta && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.4)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 50 }}>
          <div style={{ width: '90%', maxWidth: 900, background: 'white', borderRadius: 8, padding: 20, maxHeight: '80vh', overflow: 'auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h2>Libreta — {modal.libreta.alumno_nombre} — {modal.libreta.periodo_obj ? modal.libreta.periodo_obj.nombre : ''}</h2>
              <div style={{ display: 'flex', gap: 8 }}>
                {modal.libreta && modal.libreta.estado === 'REVISION_TUTOR' ? (
                  <button
                    disabled
                    title="Libreta en revisión por tutor - exportación desactivada"
                    style={{
                      padding: '6px 10px',
                      background: '#9ca3af',
                      color: 'white',
                      border: 'none',
                      borderRadius: 999,
                      fontFamily: 'inherit',
                      fontWeight: 600,
                      cursor: 'not-allowed'
                    }}
                  >Exportar PDF</button>
                ) : (
                  <button
                    onClick={exportPdf}
                    style={{
                      padding: '6px 10px',
                      background: '#2563eb',
                      color: 'white',
                      border: 'none',
                      borderRadius: 999,
                      fontFamily: 'inherit',
                      fontWeight: 600,
                      cursor: 'pointer'
                    }}
                  >Exportar PDF</button>
                )}
                <button
                  onClick={() => setModal({ open: false, libreta: null, details: null })}
                  style={{
                    padding: '6px 10px',
                    background: '#d7dae0ff',
                    color: '#0f172a',
                    border: 'none',
                    borderRadius: 999,
                    fontFamily: 'inherit',
                    fontWeight: 600,
                    cursor: 'pointer'
                  }}
                >Cerrar</button>
              </div>
            </div>

            {!modal.details && <div>Cargando...</div>}
            {modal.details && (
              <div ref={printRef} style={{ width: 760, maxWidth: '100%', margin: '0 auto', textAlign: 'center' }}>
                {/* Encabezado general centrado sobre todo el PDF */}
                {(() => {
                  const periodo = modal.libreta && modal.libreta.periodo_obj;
                  // Prefer a numeric year: accept only plausible year values (4-digit >= 1900).
                  // Try: periodo.anio_academico, periodo.anio (only if they look like a year),
                  // then extract a 4-digit year from periodo.nombre. Fallback to current year.
                  let yearLabel = (new Date()).getFullYear();
                  if (periodo) {
                    const tryVals = [periodo.anio_academico, periodo.anio];
                    let found = false;
                    for (const v of tryVals) {
                      if (v !== undefined && v !== null) {
                        const num = Number(v);
                        if (!Number.isNaN(num) && num >= 1900 && num <= 3000) {
                          yearLabel = num;
                          found = true;
                          break;
                        }
                      }
                    }
                    if (!found && periodo.nombre) {
                      const m = String(periodo.nombre).match(/(20\d{2})/);
                      if (m) {
                        yearLabel = m[1];
                        found = true;
                      }
                    }
                  }
                  const nivel = getNivelFromAula(modal.libreta && modal.libreta.aula_obj) || (modal.libreta && modal.libreta.grado_nombre) || '';
                  return (
                    <div style={{ marginBottom: 12 }}>
                      <div style={{ fontWeight: 700, fontSize: 14 }}>INSTITUCIÓN EDUCATIVA PRIVADA</div>
                      <div style={{ fontWeight: 700, fontSize: 16, marginTop: 2 }}>“CRISTO REDENTOR DE NOCHETO” EDUCACIÓN SECUNDARIA</div>
                      <div style={{ marginTop: 6 }}>DIOS, AMOR, DISCIPLINA</div>
                      <div style={{ marginTop: 4 }}>MZ J –LT 8 PSJ RASUÑITI SANTA ANITA</div>
                      <div style={{ marginTop: 4, fontStyle: 'italic' }}>“AÑO DE LA RECUPERACIÓN Y CONSOLIDACIÓN DE LA ECONOMÍA PERUANA”</div>
                      <div style={{ marginTop: 8, fontWeight: 800 }}>BOLETAS DE NOTAS {yearLabel}-EDUCACION {nivel}</div>
                    </div>
                  );
                })()}
                {/* Encabezado con datos del alumno/aula: 2 filas x 3 columnas */}
                <div style={{ marginTop: 8, marginBottom: 12 }}>
                  <table style={{ width: '100%', maxWidth: 720, borderCollapse: 'collapse', border: '1px solid #d1d5db', tableLayout: 'fixed', fontSize: '0.95rem' }}>
                    <thead>
                      <tr>
                        <th style={{ padding: 8, borderRight: '1px solid #d1d5db', fontWeight: 700, textAlign: 'center' }}>Alumno</th>
                        <th style={{ padding: 8, borderLeft: '1px solid #d1d5db', fontWeight: 700, textAlign: 'center' }}>Grado</th>
                        <th style={{ padding: 8, borderLeft: '1px solid #d1d5db', fontWeight: 700, textAlign: 'center' }}>Nivel</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td style={{ padding: 8, borderRight: '1px solid #d1d5db', textAlign: 'center' }}>{modal.libreta.alumno_nombre || ''}</td>
                        <td style={{ padding: 8, borderLeft: '1px solid #d1d5db', textAlign: 'center' }}>{modal.libreta.grado_nombre || (modal.libreta.aula_obj && modal.libreta.aula_obj.grado ? (modal.libreta.aula_obj.grado.nombre || modal.libreta.aula_nombre) : (modal.libreta.aula_nombre || ''))}</td>
                        <td style={{ padding: 8, borderLeft: '1px solid #d1d5db', textAlign: 'center' }}>
                          {(() => {
                            const nivelFromAula = getNivelFromAula(modal.libreta.aula_obj);
                            // Several fallback field names commonly used in different APIs
                            const fallbacks = [
                              nivelFromAula,
                              modal.libreta && (modal.libreta.nivel || modal.libreta.nivel_nombre || modal.libreta.aula_nivel),
                              modal.libreta && modal.libreta.nivel_obj && (modal.libreta.nivel_obj.nombre || modal.libreta.nivel_obj.nombre_nivel),
                              ''
                            ];
                            const nivel = fallbacks.find(v => v && String(v).trim() !== '');
                            return nivel || <span style={{ color: '#6b7280' }}>— Sin nivel —</span>;
                          })()}
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                {/* Removed debug block; nivel will be inferred from aula_obj.grado or grado_nombre */}

                <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: 12, tableLayout: 'fixed', fontSize: '0.95rem' }}>
                  <thead>
                    <tr>
                      <th style={{ border: '1px solid #e5e7eb', padding: 8 }}>Curso</th>
                      {modal.libreta.periodos_anio && modal.libreta.periodos_anio.map((p, idx) => (
                        <th key={p.id} style={{ border: '1px solid #e5e7eb', padding: 8, textAlign: 'center' }}>{p.nombre}</th>
                      ))}
                      <th style={{ border: '1px solid #e5e7eb', padding: 8, textAlign: 'center' }}>Promedio Final</th>
                    </tr>
                  </thead>
                  <tbody>
                    {modal.details.table.map(row => (
                      <tr key={row.asignId}>
                        <td style={{ border: '1px solid #e5e7eb', padding: 8 }}>{row.nombre}</td>
                        {row.bimestres.map((b, i) => (
                          <td key={i} style={{ border: '1px solid #e5e7eb', padding: 8, textAlign: 'center' }}>{b !== null ? b : '-'}</td>
                        ))}
                        <td style={{ border: '1px solid #e5e7eb', padding: 8, textAlign: 'center' }}>
                          {(() => {
                            const nums = row.bimestres.filter(v => v !== null).map(v => Number(v));
                            if (nums.length === 0) return '-';
                            const avg = nums.reduce((a, b) => a + b, 0) / nums.length;
                            return avg.toFixed(2);
                          })()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                  <tfoot>
                    <tr>
                      <td style={{ border: '1px solid #e5e7eb', padding: 8, fontWeight: 700 }} colSpan={modal.libreta && modal.libreta.periodos_anio ? (modal.libreta.periodos_anio.length + 1) : 2}>Promedio Final del Bimestre</td>
                      <td style={{ border: '1px solid #e5e7eb', padding: 8, textAlign: 'center', fontWeight: 700 }}>
                        {(() => {
                          const rows = (modal.details && modal.details.table) || [];
                          if (!rows.length) return '-';
                          const suma = rows.reduce((acc, r) => {
                            const nums = (r.bimestres || []).filter(v => v !== null).map(v => Number(v));
                            let rowAvg = 0;
                            if (nums.length > 0) rowAvg = nums.reduce((a, b) => a + b, 0) / nums.length;
                            return acc + rowAvg;
                          }, 0);
                          const totalCursos = rows.length;
                          const resultado = suma / totalCursos;
                          return Number.isFinite(resultado) ? resultado.toFixed(2) : '-';
                        })()}
                      </td>
                    </tr>
                  </tfoot>
                </table>

                {/* Mostrar observación del tutor (solo lectura) y puesto */}
                <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, marginTop: 14 }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 700, marginBottom: 6 }}>Observación del Tutor</div>
                    <div style={{ minHeight: 64, padding: 10, border: '1px solid #e5e7eb', borderRadius: 6, background: '#fafafa', whiteSpace: 'pre-wrap' }}>
                      {modal.libreta && (modal.libreta.observacion_tutor || modal.libreta.observacion || modal.libreta.tutor_comentario) ? (
                        modal.libreta.observacion_tutor || modal.libreta.observacion || modal.libreta.tutor_comentario
                      ) : (
                        <span style={{ color: '#6b7280' }}>— Sin observación —</span>
                      )}
                    </div>
                  </div>

                  <div style={{ width: 220 }}>
                    <div style={{ fontWeight: 700, marginBottom: 6, textAlign: 'right' }}>Puesto en el Aula</div>
                    <div style={{ minHeight: 64, padding: 10, border: '1px solid #e5e7eb', borderRadius: 6, background: '#fff', textAlign: 'center', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.1rem' }}>
                      {modal.libreta && (modal.libreta.puesto !== undefined && modal.libreta.puesto !== null) ? modal.libreta.puesto : <span style={{ color: '#6b7280' }}>—</span>}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default LibretasBimestrales;
