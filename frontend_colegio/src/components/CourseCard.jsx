import React from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import bookIcon from '../assets/icons/book.svg';

const CourseCard = ({ curso }) => {
  const navigate = useNavigate();

  // Función para ir al registro de notas
  const handleEnter = () => {
    // Navegamos a una ruta dinámica (ej: /notas/15)
    navigate(`/notas/${curso.id}`);
  };

  return (
    <div style={{
      background: 'white',
      borderRadius: '12px',
      padding: '20px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
      border: '1px solid #e5e7eb',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'space-between',
      minHeight: '180px',
      position: 'relative'
    }}>
      
      {/* Encabezado con Icono */}
      <div style={{ display: 'flex', gap: '15px', alignItems: 'flex-start' }}>
        <div style={{
          background: '#fff7ed',
          width: '50px',
          height: '50px',
          borderRadius: '10px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <img src={bookIcon} alt="book" style={{ width: 28, height: 28 }} />
        </div>
        <div>
          <h3 style={{ margin: '0 0 5px', color: '#1f2937', fontSize: '1.1rem' }}>
            {curso.curso_nombre}
          </h3>
          <span style={{ 
            background: '#eff6ff', 
            color: '#2563eb', 
            padding: '4px 8px', 
            borderRadius: '4px', 
            fontSize: '0.75rem', 
            fontWeight: 'bold' 
          }}>
            {curso.aula_nombre} - {curso.grado}
          </span>
        </div>
      </div>

      {/* Barra de Progreso Simulada */}
      <div style={{ marginTop: '20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '5px', color: '#6b7280' }}>
          <span>Progreso de notas</span>
          <span>75%</span>
        </div>
        <div style={{ width: '100%', height: '8px', background: '#f3f4f6', borderRadius: '4px' }}>
          <div style={{ width: '75%', height: '100%', background: '#f97316', borderRadius: '4px' }}></div>
        </div>
      </div>

      {/* Botón de Acción */}
      <div style={{ display: 'flex', gap: 8, marginTop: '20px' }}>
        <button 
          onClick={handleEnter}
          className="btn-primary" 
          style={{ padding: '8px', flex: 1 }}
        >
          Registrar Notas
        </button>

        <button 
          onClick={async () => {
            if (!confirm('¿Enviar promedios de este curso al tutor?')) return;
              try {
              // Obtener periodo activo
              const res = await api.get('periodos/?activo=true');
              let periodoId = null;
              if (res.data && res.data.length > 0) periodoId = res.data[0].id;
              const body = periodoId ? { periodo: periodoId } : {};
              await api.post(`cursos-asignados/${curso.id}/enviar_promedios/`, body);
              // evitar notificación de éxito; registrar en consola
              console.log('Promedios enviados correctamente');
            } catch (err) {
              console.error(err);
              alert('Error enviando promedios. Revisa la consola.');
            }
          }}
          style={{ padding: '8px', background: 'white', border: '1px solid #e5e7eb', color: '#374151', borderRadius: 8, cursor: 'pointer' }}
        >
          Enviar Promedios
        </button>
      </div>
    </div>
  );
};

export default CourseCard;