import React, { useState } from 'react';
import api from '../services/api';
import { useNavigate } from 'react-router-dom';
import { FaGraduationCap } from 'react-icons/fa';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      // 1. Pedimos el token a Django
      const response = await api.post('token/', {
        username: username,
        password: password
      });

      // 2. Guardamos el token en el navegador
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);

      // 3. Consultamos QUIÉN es el usuario (Rol)
      // Como ya tenemos token, el interceptor de api.js lo enviará aquí
      console.log("Token obtenido, consultando rol...");
      const infoResponse = await api.get('user-info/');
      
      const esAdmin = infoResponse.data.es_admin;
      const nombreUsuario = infoResponse.data.nombre_completo;

      console.log("Rol Admin:", esAdmin);
      
      // Guardamos datos útiles
      localStorage.setItem('es_admin', esAdmin);
      localStorage.setItem('user_name', nombreUsuario);

      // 4. Redirigimos según el rol
      // No mostrar alertas de éxito; registrar en consola
      console.log(`Login correcto: ${nombreUsuario}`);
      
      if (esAdmin) {
        navigate('/admin'); // Directora
      } else {
        navigate('/dashboard'); // Profesora
      }

    } catch (error) {
      console.error("Error de login:", error);
      alert("Credenciales incorrectas o error de conexión.");
    }
  };

  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      height: '100vh', 
      background: '#f0f2f5',
      backgroundImage: 'radial-gradient(#cbd5e1 1px, transparent 1px)',
      backgroundSize: '20px 20px'
    }}>
      
      <div style={{
        background: 'white',
        padding: '40px',
        borderRadius: '12px',
        boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
        width: '100%',
        maxWidth: '400px',
        textAlign: 'center'
      }}>
        
        <div style={{ marginBottom: '30px' }}>
          <div style={{ 
            background: '#f8fafc', 
            width: '80px', 
            height: '80px', 
            borderRadius: '50%', 
            margin: '0 auto 15px',
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center'
          }}>
             <FaGraduationCap size={40} color="var(--color-primary)" />
          </div>
          
          <h3 style={{ margin: '0', color: '#1e293b' }}>INTRANET ACADÉMICA</h3>
          <h2 style={{ margin: '5px 0 0', color: '#0F6236', fontSize: '1.2rem' }}>
            IEP CRISTO REDENTOR
          </h2>
        </div>

        <form onSubmit={handleLogin} style={{ textAlign: 'left' }}>
          <label style={{ fontSize: '0.9rem', color: '#64748b' }}>Usuario</label>
          <input 
            type="text" 
            placeholder="Ingrese su usuario" 
            className="input-field"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />

          <label style={{ fontSize: '0.9rem', color: '#64748b' }}>Contraseña</label>
          <input 
            type="password" 
            placeholder="Ingrese su contraseña" 
            className="input-field"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <button type="submit" className="btn-primary" style={{ marginTop: '10px' }}>
            Ingresar
          </button>
        </form>

        <p style={{ marginTop: '20px', color: '#ef4444', fontSize: '0.85rem', cursor: 'pointer' }}>
          ¿Olvidó su contraseña?
        </p>
      </div>
    </div>
  );
};

export default Login;