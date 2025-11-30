import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import CourseCard from '../components/CourseCard';

const Dashboard = () => {
  const navigate = useNavigate();
  const [cursos, setCursos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [userInfo, setUserInfo] = useState(null);

  // Cargar cursos al entrar
  useEffect(() => {
    const fetchCursos = async () => {
      try {
        const response = await api.get('cursos-asignados/');
        const cursosList = Array.isArray(response.data) ? response.data : (response.data && Array.isArray(response.data.results) ? response.data.results : []);
        setCursos(cursosList);
      } catch (error) {
        console.error("Error cargando cursos", error);
      } finally {
        setLoading(false);
      }
    };
    fetchCursos();
    // Obtener info de usuario
    (async () => {
      try {
        const r = await api.get('user-info/');
        setUserInfo(r.data);
      } catch (err) {
        console.error('Error user-info', err);
      }
    })();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    navigate('/login');
  };

  return (
    <div style={{ display: 'flex', height: '100vh', fontFamily: 'sans-serif' }}>
      
      {/* SIDEBAR (Igual que antes) */}
      <div style={{ width: '250px', background: 'white', borderRight: '1px solid #e5e7eb', padding: '20px', position: 'relative' }}>
        {/* CABECERA: logo circular y texto en verde (sobre fondo claro) */}
        <div style={{ marginBottom: '60px', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ width: '36px', height: '36px', background: '#0F6236', borderRadius: '50%', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700 }}>
            CR
          </div>
          <div>
            <div style={{ fontSize: '0.95rem', color: '#0F6236', fontWeight: 600 }}>IEP Cristo Redentor</div>
            <div style={{ fontSize: '0.85rem', color: '#0F6236' }}>Intranet Académica</div>
          </div>
        </div>

        <ul style={{ listStyle: 'none', padding: 0, marginTop: '22px' }}>
          <li style={{ padding: '10px', background: '#ecfdf5', borderRadius: '8px', marginBottom: '10px', fontWeight: '700', color: '#065f46' }}>Mis Cursos</li>
          {userInfo && userInfo.es_tutor && (
            <li style={{ padding: '10px', marginTop: '10px', cursor: 'pointer', borderRadius: '6px' }} onMouseOver={(e) => e.currentTarget.style.background = '#ecfdf5'} onMouseOut={(e) => e.currentTarget.style.background = 'transparent'} onClick={() => navigate('/mis-tutorias')}>Mis Tutorías</li>
          )}
          {userInfo && userInfo.es_directora && (
            <li style={{ padding: '10px', marginTop: '10px', cursor: 'pointer', borderRadius: '6px' }} onMouseOver={(e) => e.currentTarget.style.background = '#ecfdf5'} onMouseOut={(e) => e.currentTarget.style.background = 'transparent'} onClick={() => navigate('/admin/periodos')}>Gestionar Períodos</li>
          )}
        </ul>

        <button onClick={handleLogout} style={{ position: 'absolute', bottom: '30px', left: '20px', color: '#dc2626', background: 'none', border: 'none', cursor: 'pointer' }}>Cerrar Sesión</button>
      </div>

      {/* CONTENIDO PRINCIPAL */}
      <div style={{ flex: 1, background: '#f9fafb', padding: '30px', overflowY: 'auto' }}>
        
        <header style={{ marginBottom: '30px' }}>
          <h1 style={{ margin: 0, fontSize: '1.5rem', color: '#111' }}>Mis Asignaturas</h1>
          <p style={{ color: '#666' }}>Seleccione su curso a cargo para registrar notas</p>
        </header>

        {/* GRILLA DE CURSOS */}
        {loading ? (
          <p>Cargando cursos...</p>
        ) : (
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', 
            gap: '20px' 
          }}>
            {cursos.length > 0 ? (
              cursos.map(curso => (
                <CourseCard key={curso.id} curso={curso} />
              ))
            ) : (
              <p>No tienes cursos asignados.</p>
            )}
          </div>
        )}

      </div>
    </div>
  );
};

export default Dashboard;