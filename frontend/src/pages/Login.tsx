import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { apiClient } from '../api/client';
import { HeartPulse } from 'lucide-react';

export const Login = () => {
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await apiClient.post('/auth/login', formData);
      localStorage.setItem('token', response.data.access_token);
      window.dispatchEvent(new Event('storage')); // trigger auth state re-render
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid credentials');
    }
  };

  return (
    <div className="min-h-screen flex flex-col justify-center items-center p-6 bg-brand-50">
      <div className="w-full max-w-md bg-white border border-brand-100 shadow-sm p-8">
        <div className="flex justify-center mb-6">
          <div className="w-12 h-12 bg-brand-600 flex items-center justify-center">
            <HeartPulse className="text-white w-6 h-6" />
          </div>
        </div>
        <h2 className="text-2xl font-semibold text-center text-slate-800 mb-6">Welcome Back</h2>
        {error && <div className="bg-red-50 text-red-600 p-3 mb-4 text-sm border border-red-100">{error}</div>}
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Email</label>
            <input
              type="email"
              required
              className="w-full border border-slate-300 p-3 text-slate-900 focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500"
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Password</label>
            <input
              type="password"
              required
              className="w-full border border-slate-300 p-3 text-slate-900 focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500"
              value={formData.password}
              onChange={(e) => setFormData({...formData, password: e.target.value})}
            />
          </div>
          <button type="submit" className="w-full bg-brand-600 text-white font-medium py-3 mt-4 hover:bg-brand-700 transition-colors">
            Log In
          </button>
        </form>
        
        <p className="mt-6 text-center text-sm text-slate-600">
          Don't have an account? <Link to="/register" className="text-brand-600 font-medium hover:underline">Sign up</Link>
        </p>
      </div>
    </div>
  );
};
