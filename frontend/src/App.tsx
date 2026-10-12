import { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import AnalyzeText from './pages/AnalyzeText';
import Login from './pages/Login';
import Signup from './pages/Signup';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const handleLogin = () => setIsAuthenticated(true);
  const handleLogout = () => setIsAuthenticated(false);

  // A simple wrapper to protect routes
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

        {/* Protected Routes inside the Layout */}
        <Route 
          path="/" 
          element={
            <ProtectedRoute>
              {/* Pass handleLogout to Layout if we want to logout from Navbar in the future */}
              <Layout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Dashboard />} />
          <Route path="analyze/text" element={<AnalyzeText />} />
          <Route path="analyze/image" element={<div className="p-6 text-gray-500 font-medium">Image Analysis Development Area (Phase 5)</div>} />
          <Route path="analyze/video" element={<div className="p-6 text-gray-500 font-medium">Video Analysis Development Area (Phase 6)</div>} />
          <Route path="analyze/audio" element={<div className="p-6 text-gray-500 font-medium">Audio Analysis Development Area (Phase 7)</div>} />
          <Route path="fact-check" element={<div className="p-6 text-gray-500 font-medium">Fact-Checking Engine (Phase 8)</div>} />
          <Route path="history" element={<div className="p-6 text-gray-500 font-medium">Analysis History Logging Area</div>} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
