import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import bookIcon from '../assets/icons/book.svg';
import teacherIcon from '../assets/icons/teacher.svg';
import usersIcon from '../assets/icons/users.svg';
import docIcon from '../assets/icons/doc.svg';

const AdminDashboard = () => {
  const navigate = useNavigate();
  const [alumnosCount, setAlumnosCount] = useState(0);
  const [profesoresCount, setProfesoresCount] = useState(0);

  useEffect(() => {
    const fetchCounts = async () => {
      const getCountFromResponse = (data) => {
        if (!data) return 0;
        if (Array.isArray(data)) return data.length;
        if (data && Array.isArray(data.results)) return data.results.length;
        if (data && typeof data.count === 'number') return data.count;
        return 0;
      };

      try {
        const resAlumnos = await api.get('alumnos/');
        setAlumnosCount(getCountFromResponse(resAlumnos.data));
      } catch (err) {
        console.error('Error fetching alumnos count', err);
        setAlumnosCount('N/A');
      }
      try {
        const resProfes = await api.get('profesores/');
        setProfesoresCount(getCountFromResponse(resProfes.data));
      } catch (err) {
        console.error('Error fetching profesores count', err);
        setProfesoresCount('N/A');
      }
    };
    fetchCounts();
  }, []);

  const handleLogout = () => {
    localStorage.clear();
    navigate('/login');
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh', fontFamily: 'inherit', background: '#f9fafb' }}>
      
      {/* SIDEBAR VERDE */}
      <div style={{ width: '260px', background: '#0F6236', color: 'white', padding: '20px' }}>
        <div style={{ marginBottom: '40px', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ width: '40px', height: '40px', background: 'white', borderRadius: '50%', color: '#0F6236', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>
            CR
          </div>
          <div>
            <div style={{ fontSize: '0.9rem', opacity: 0.8 }}>IEP Cristo Redentor</div>
            <div style={{ fontSize: '0.8rem' }}>Intranet Académica</div>
          </div>
        </div>

        <nav>
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {/* ENLACE INICIO */}
            <li 
              onClick={() => navigate('/admin')}
              style={{ padding: '12px', background: 'rgba(255,255,255,0.1)', borderRadius: '8px', marginBottom: '8px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '10px' }}
            >
              Inicio
            </li>

            {/* ENLACE GESTIÓN DE CUENTAS (CORREGIDO) */}
            <li 
              onClick={() => navigate('/admin/gestion')} 
              style={{ padding: '12px', opacity: 0.9, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '10px', transition: '0.3s' }}
              onMouseOver={(e) => e.currentTarget.style.opacity = 1}
              onMouseOut={(e) => e.currentTarget.style.opacity = 0.9}
            >
              Gestión de Cuentas
            </li>

            <li 
              onClick={() => navigate('/admin/periodos')}
              style={{ padding: '12px', opacity: 0.9, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '10px', transition: '0.3s' }}
              onMouseOver={(e) => e.currentTarget.style.opacity = 1}
              onMouseOut={(e) => e.currentTarget.style.opacity = 0.9}
            >
              Gestión de Períodos
            </li>

            <li 
              onClick={() => navigate('/admin/libretas')}
              style={{ padding: '12px', opacity: 0.9, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '10px' }}>
              Libretas Bimestrales
            </li>
          </ul>
        </nav>

        <button 
          onClick={handleLogout}
          style={{ padding: '12px',marginTop: 'auto', color: '#fca5a5', background: 'none', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '10px', position: 'absolute', bottom: '30px' }}
        >
           Cerrar Sesión
        </button>
      </div>

      {/* CONTENIDO PRINCIPAL */}
      <div style={{ flex: 1, padding: '40px' }}>
        
        <header style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '40px' }}>
          <div>
            <h1 style={{ margin: 0, fontSize: '1.8rem', color: '#1f2937' }}>Bienvenida de vuelta, Directora</h1>
            <p style={{ color: '#6b7280', marginTop: '5px' }}>Gestión administrativa y seguimiento académico</p>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
             <div style={{ textAlign: 'right' }}>
                <div style={{ fontWeight: 'bold', color: '#1f2937' }}>María Sánchez</div>
                <div style={{ fontSize: '0.8rem', color: '#6b7280' }}>Directora General</div>
             </div>
             <div style={{ width: '45px', height: '45px', background: '#0F6236', color: 'white', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>DT</div>
          </div>
        </header>

        {/* TARJETAS DE ESTADÍSTICAS */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '20px', marginBottom: '40px' }}>
          <StatCard icon={<img src={bookIcon} alt="book" style={{ width: 28, height: 28 }} />} title="Número de Alumnos" value={alumnosCount} subtitle="Total matriculados" color="#0F6236" />
          <StatCard icon={<img src={teacherIcon} alt="teacher" style={{ width: 28, height: 28 }} />} title="Número de Profesores" value={profesoresCount} subtitle="Total registrados" color="#3b82f6" />
        </div>

        {/* ACCIONES / NAVEGACIÓN */}
        <h3 style={{ color: '#374151', marginBottom: '20px' }}>Opciones</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '20px' }}>
           <button 
             onClick={() => navigate('/admin/aulas')}
             style={{
               height: '100px',
               background: '#eef6ff',
               border: '1px solid rgba(14, 165, 233, 0.12)',
               borderRadius: '8px',
               fontSize: '1.1rem',
               cursor: 'pointer',
               color: '#0f172a',
               display: 'flex',
               flexDirection: 'column',
               alignItems: 'center',
               justifyContent: 'center',
               gap: '8px'
             }}
           >
             Ver Aulas y Alumnos
             <span style={{fontSize: '0.85rem', color: '#475569'}}>Ver todas las aulas con sus estudiantes y tutores</span>
           </button>

           <button 
             onClick={() => navigate('/admin/gestion')}
             style={{
               height: '100px',
               background: '#f0fdf4',
               border: '1px solid rgba(16, 185, 129, 0.08)',
               borderRadius: '8px',
               fontSize: '1.1rem',
               cursor: 'pointer',
               color: '#0f172a',
               display: 'flex',
               flexDirection: 'column',
               alignItems: 'center',
               justifyContent: 'center',
               gap: '8px'
             }}
           >
             Gestión General
             <span style={{fontSize: '0.85rem', color: '#475569'}}>Alumnos, Profes y Cursos</span>
           </button>
        </div>

      </div>
    </div>
  );
};

// Componente simple para las tarjetas
const StatCard = ({ icon, title, value, subtitle, color }) => (
  <div style={{ background: 'white', padding: '22px', borderRadius: '12px', border: '2px solid #fb923c', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', height: '140px' }}>
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
      <span style={{ color: '#6b7280', fontSize: '1.05rem', fontWeight: 600 }}>{title}</span>
      <span style={{ color: color, fontSize: '1.6rem' }}>{icon}</span>
    </div>
    <div>
      <div style={{ fontSize: '2.4rem', fontWeight: '700', color: '#1f2937' }}>{value}</div>
      <div style={{ fontSize: '0.85rem', color: '#9ca3af' }}>{subtitle}</div>
    </div>
  </div>
);

export default AdminDashboard;