import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '../api/client';
import { LogOut, LayoutDashboard, Stethoscope, Activity } from 'lucide-react';

export const Dashboard = () => {
  const navigate = useNavigate();
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const resp = await apiClient.get('/profile/me');
        setProfile(resp.data);
      } catch (err: any) {
        if (err.response?.status === 401) {
          // Invalid token, logout
          localStorage.removeItem('token');
          window.dispatchEvent(new Event('storage'));
          navigate('/login');
        } else if (err.response?.status === 404) {
          // Profile not found, force them to onboarding
          navigate('/welcome');
        } else {
          console.error("Failed to load profile", err);
        }
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    window.dispatchEvent(new Event('storage'));
    navigate('/login');
  };

  if (loading) {
    return <div className="min-h-screen bg-brand-50 flex items-center justify-center text-slate-500">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-brand-50 flex flex-col">
      {/* Navbar */}
      <nav className="bg-white border-b border-brand-100 px-6 py-4 flex justify-between items-center">
        <div className="flex items-center space-x-2 text-brand-700">
          <LayoutDashboard className="w-6 h-6" />
          <span className="font-semibold text-lg tracking-tight">Health AI</span>
        </div>
        <button 
          onClick={handleLogout}
          className="text-slate-500 hover:text-brand-600 flex items-center space-x-2 text-sm font-medium transition-colors"
        >
          <span>Log Out</span>
          <LogOut className="w-4 h-4" />
        </button>
      </nav>

      {/* Main Content */}
      <main className="flex-1 p-6 max-w-4xl w-full mx-auto mt-6">
        <h1 className="text-3xl font-semibold text-slate-800 mb-2">Welcome Back</h1>
        <p className="text-slate-600 mb-10">Select a module to continue your care journey.</p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          {/* Triage Module Card */}
          <div 
            onClick={() => navigate('/triage')}
            className="bg-white border border-brand-100 p-8 hover:shadow-md transition-shadow group cursor-pointer"
          >
            <div className="w-12 h-12 bg-brand-50 flex items-center justify-center mb-6 group-hover:bg-brand-100 transition-colors">
              <Stethoscope className="w-6 h-6 text-brand-600" />
            </div>
            <h3 className="text-xl font-medium text-slate-800 mb-2">Symptom Checker</h3>
            <p className="text-slate-600 text-sm leading-relaxed">
              Feeling unwell? Describe your symptoms to our AI triage engine to get an instant risk assessment.
            </p>
          </div>

          {/* Chronic Module Card */}
          <div className="bg-white border border-brand-100 p-8 hover:shadow-md transition-shadow group cursor-pointer">
            <div className="w-12 h-12 bg-brand-50 flex items-center justify-center mb-6 group-hover:bg-brand-100 transition-colors">
              <Activity className="w-6 h-6 text-brand-600" />
            </div>
            <h3 className="text-xl font-medium text-slate-800 mb-2">Chronic Companion</h3>
            <p className="text-slate-600 text-sm leading-relaxed">
              Log your daily vitals and get personalized AI insights for your long-term health condition.
            </p>
          </div>

        </div>
      </main>
    </div>
  );
};
