import { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import AnalyzeText from './pages/AnalyzeText';
import AnalyzeImage from './pages/AnalyzeImage';
import AnalyzeVideo from './pages/AnalyzeVideo';
import AnalyzeAudio from './pages/AnalyzeAudio';
import FactCheck from './pages/FactCheck';
import History from './pages/History';
import Login from './pages/Login';
import Signup from './pages/Signup';

function App() {
  const [userName, setUserName] = useState<string>(() => {
    return localStorage.getItem('truthguard_user') || 'Admin User';
  });
  
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(() => {
    // Default to true for ease of review or check localStorage
    return localStorage.getItem('truthguard_auth') !== 'false';
  });

  const handleLogin = (name: string) => {
    setUserName(name);
    setIsAuthenticated(true);
    localStorage.setItem('truthguard_user', name);
    localStorage.setItem('truthguard_auth', 'true');
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    localStorage.removeItem('truthguard_token');
    localStorage.setItem('truthguard_auth', 'false');
  };

  const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
    if (!isAuthenticated) {
      return <Navigate to="/login" replace />;
    }
    return <>{children}</>;
  };

  return (
    <BrowserRouter>
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={<Login onLogin={handleLogin} />} />
        <Route path="/signup" element={<Signup onLogin={handleLogin} />} />

        {/* Protected Application Routes */}
        <Route 
          path="/" 
          element={
            <ProtectedRoute>
              <Layout userName={userName} onLogout={handleLogout} />
            </ProtectedRoute>
          }
        >
          <Route index element={<Dashboard />} />
          <Route path="analyze/text" element={<AnalyzeText />} />
          <Route path="analyze/image" element={<AnalyzeImage />} />
          <Route path="analyze/video" element={<AnalyzeVideo />} />
          <Route path="analyze/audio" element={<AnalyzeAudio />} />
          <Route path="fact-check" element={<FactCheck />} />
          <Route path="history" element={<History />} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
