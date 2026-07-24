import React from 'react';
import { useNavigate } from 'react-router-dom';
import { HeartPulse } from 'lucide-react';

export const Welcome = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6 bg-brand-50">
      <div className="w-full max-w-md bg-white border border-brand-100 shadow-sm p-8 flex flex-col items-center text-center">
        <div className="w-16 h-16 bg-brand-100 flex items-center justify-center mb-6">
          <HeartPulse className="w-8 h-8 text-brand-600" />
        </div>
        <h1 className="text-2xl font-semibold mb-4 text-slate-800">
          Thanks for joining us!
        </h1>
        <p className="text-slate-600 mb-8 leading-relaxed">
          We're thrilled to have you here. To provide you with the most accurate AI triage and personalized health nudges, we'd like to ask a few quick questions about your health background.
        </p>
        <button
          onClick={() => navigate('/onboarding')}
          className="w-full bg-brand-600 text-white font-medium py-3 hover:bg-brand-700 transition-colors"
        >
          Let's Get Started
        </button>
      </div>
    </div>
  );
};
