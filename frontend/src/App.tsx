import { useState, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { OnboardingWizard } from './pages/OnboardingWizard';
import { Dashboard } from './pages/Dashboard';
import { Welcome } from './pages/Welcome';
import { TriageChat } from './pages/TriageChat';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem('token'));

  useEffect(() => {
    const handleStorageChange = () => {
      setIsAuthenticated(!!localStorage.getItem('token'));
    };
    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  return (
    <div className="min-h-screen bg-brand-50 font-sans text-slate-900">
      <Routes>
        {/* Public Auth Routes */}
        <Route path="/login" element={!isAuthenticated ? <Login /> : <Navigate to="/" />} />
        <Route path="/register" element={!isAuthenticated ? <Register /> : <Navigate to="/" />} />

        {/* Onboarding Flow */}
        <Route path="/welcome" element={isAuthenticated ? <Welcome /> : <Navigate to="/login" />} />
        <Route path="/onboarding" element={isAuthenticated ? <OnboardingWizard /> : <Navigate to="/login" />} />

        {/* Protected Dashboard Route */}
        <Route path="/" element={isAuthenticated ? <Dashboard /> : <Navigate to="/login" />} />
        
        {/* Modules */}
        <Route path="/triage" element={isAuthenticated ? <TriageChat /> : <Navigate to="/login" />} />
      </Routes>
    </div>
  );
}

export default App;
