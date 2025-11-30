import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

// Importación de tus páginas
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import RegistroNotas from './pages/RegistroNotas';
import AdminDashboard from './pages/AdminDashboard';
import GestionDatos from './pages/GestionDatos'; // <--- Importamos la página de gestión
import AulasList from './pages/AulasList';
import MisTutorias from './pages/MisTutorias';
import GestionPeriodos from './pages/GestionPeriodos';
import LibretasBimestrales from './pages/LibretasBimestrales';

// --- COMPONENTE DE SEGURIDAD ---
// Este componente verifica si existe el token. Si no, manda al Login.
const PrivateRoute = ({ children }) => {
  const token = localStorage.getItem('access_token');
  return token ? children : <Navigate to="/login" replace />;
};

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* RUTA PÚBLICA: Login */}
        <Route path="/login" element={<Login />} />

        {/* --- RUTAS PROTEGIDAS (Solo usuarios logueados) --- */}
        
        {/* 1. Dashboard Principal (Para Profesoras) */}
        <Route 
          path="/dashboard" 
          element={
            <PrivateRoute>
              <Dashboard />
            </PrivateRoute>
          } 
        />

        {/* 2. Registro de Notas (Ruta dinámica: cambia según el curso) */}
        <Route 
          path="/notas/:idCurso" 
          element={
            <PrivateRoute>
              <RegistroNotas />
            </PrivateRoute>
          } 
        />

        {/* 3. Dashboard Directora */}
        <Route 
          path="/admin" 
          element={
            <PrivateRoute>
              <AdminDashboard />
            </PrivateRoute>
          } 
        />

        {/* 4. Gestión de Datos (Crear alumnos, cursos, aulas - Solo Directora) */}
        <Route 
          path="/admin/gestion" 
          element={
            <PrivateRoute>
              <GestionDatos />
            </PrivateRoute>
          } 
        />

        <Route 
          path="/admin/periodos" 
          element={
            <PrivateRoute>
              <GestionPeriodos />
            </PrivateRoute>
          } 
        />

        <Route 
          path="/admin/libretas" 
          element={
            <PrivateRoute>
              <LibretasBimestrales />
            </PrivateRoute>
          } 
        />

        {/* 5. Listado de Aulas */}
        <Route 
          path="/admin/aulas" 
          element={
            <PrivateRoute>
              <AulasList />
            </PrivateRoute>
          } 
        />
        <Route 
          path="/mis-tutorias"
          element={
            <PrivateRoute>
              <MisTutorias />
            </PrivateRoute>
          }
        />

        {/* RUTA POR DEFECTO: Si la ruta no existe, ir al login */}
        <Route path="*" element={<Navigate to="/login" replace />} />

      </Routes>
    </BrowserRouter>
  );
}

export default App;