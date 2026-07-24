import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { apiClient } from '../api/client';
import { ArrowRight, Check } from 'lucide-react';

const steps = [
  { id: 'demographics', title: 'Basic Demographics' },
  { id: 'physical', title: 'Physical Stats' },
  { id: 'background', title: 'Background' },
  { id: 'medical_history', title: 'Medical History' },
  { id: 'medications', title: 'Current Medications' }
];

export const OnboardingWizard = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState({
    age: 30,
    gender: 1, // 0: Female, 1: Male, 2: Other
    height_m: 1.75,
    weight_kg: 70.0,
    race: 0, // 0: Asian, 1: White, 2: Black, 3: Hispanic, 4: Other
    lang: 0, // 0: English, 1: Spanish, 2: Hindi, 3: Other
    insurance_status: 0, // 0: Medicare, 1: Medicaid, 2: Private, 3: Uninsured
    previous_ed_visits: 0,
    previous_admissions: 0,
    // Medical Conditions (0.0 or 1.0)
    asthma: 0.0,
    copd: 0.0,
    diabetes: 0.0,
    hypertension: 0.0,
    heart_disease: 0.0,
    chf: 0.0,
    kidney_disease: 0.0,
    epilepsy: 0.0,
    anemia: 0.0,
    influenza: 0.0,
    uti: 0.0,
    dizziness: 0.0,
    fatigue: 0.0,
    allergy: 0.0,
    // Medications (0.0 or 1.0)
    takes_antihypertensive: 0.0,
    takes_diabetes_medicine: 0.0,
    takes_inhaler: 0.0,
    takes_blood_thinner: 0.0
  });

  const handleNext = async () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(curr => curr + 1);
    } else {
      try {
        await apiClient.post('/profile', formData);
        navigate('/');
      } catch (err) {
        console.error("Failed to save profile", err);
        alert("Failed to save profile. Please try again.");
      }
    }
  };

  const handleCheckboxChange = (field: keyof typeof formData) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [field]: e.target.checked ? 1.0 : 0.0 });
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Age</label>
              <input type="number" className="w-full border border-slate-300 p-3" value={formData.age} onChange={(e) => setFormData({...formData, age: Number(e.target.value)})} />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Gender</label>
              <select className="w-full border border-slate-300 p-3 bg-white" value={formData.gender} onChange={(e) => setFormData({...formData, gender: Number(e.target.value)})}>
                <option value={1}>Male</option>
                <option value={0}>Female</option>
                <option value={2}>Other</option>
              </select>
            </div>
          </div>
        );
      case 1:
        return (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Height (meters)</label>
              <input type="number" step="0.01" className="w-full border border-slate-300 p-3" value={formData.height_m} onChange={(e) => setFormData({...formData, height_m: Number(e.target.value)})} />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Weight (kg)</label>
              <input type="number" step="0.1" className="w-full border border-slate-300 p-3" value={formData.weight_kg} onChange={(e) => setFormData({...formData, weight_kg: Number(e.target.value)})} />
            </div>
          </div>
        );
      case 2:
        return (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Race / Ethnicity</label>
              <select className="w-full border border-slate-300 p-3 bg-white" value={formData.race} onChange={(e) => setFormData({...formData, race: Number(e.target.value)})}>
                <option value={0}>Asian</option>
                <option value={1}>White</option>
                <option value={2}>Black</option>
                <option value={3}>Hispanic</option>
                <option value={4}>Other</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Primary Language</label>
              <select className="w-full border border-slate-300 p-3 bg-white" value={formData.lang} onChange={(e) => setFormData({...formData, lang: Number(e.target.value)})}>
                <option value={0}>English</option>
                <option value={1}>Spanish</option>
                <option value={2}>Hindi</option>
                <option value={3}>Other</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Insurance Status</label>
              <select className="w-full border border-slate-300 p-3 bg-white" value={formData.insurance_status} onChange={(e) => setFormData({...formData, insurance_status: Number(e.target.value)})}>
                <option value={0}>Medicare</option>
                <option value={1}>Medicaid</option>
                <option value={2}>Private</option>
                <option value={3}>Uninsured</option>
              </select>
            </div>
          </div>
        );
      case 3:
        return (
          <div className="space-y-4">
            <p className="text-sm text-slate-600 mb-4">Check any conditions that apply to you:</p>
            <div className="grid grid-cols-2 gap-4">
              {[
                { label: 'Asthma', field: 'asthma' },
                { label: 'COPD', field: 'copd' },
                { label: 'Diabetes', field: 'diabetes' },
                { label: 'Hypertension', field: 'hypertension' },
                { label: 'Heart Disease', field: 'heart_disease' },
                { label: 'CHF', field: 'chf' },
                { label: 'Kidney Disease', field: 'kidney_disease' },
                { label: 'Epilepsy', field: 'epilepsy' },
                { label: 'Anemia', field: 'anemia' },
                { label: 'Allergy', field: 'allergy' },
              ].map((item) => (
                <label key={item.field} className="flex items-center space-x-3 p-3 border border-slate-200 cursor-pointer hover:bg-slate-50 transition-colors">
                  <input
                    type="checkbox"
                    className="w-4 h-4 text-brand-600 border-slate-300 rounded-none focus:ring-brand-500"
                    checked={formData[item.field as keyof typeof formData] === 1.0}
                    onChange={handleCheckboxChange(item.field as keyof typeof formData)}
                  />
                  <span className="text-sm font-medium text-slate-700">{item.label}</span>
                </label>
              ))}
            </div>
          </div>
        );
      case 4:
        return (
          <div className="space-y-4">
            <p className="text-sm text-slate-600 mb-4">Are you currently taking any of these medications?</p>
            <div className="grid grid-cols-1 gap-4">
              {[
                { label: 'Blood Pressure / Antihypertensive', field: 'takes_antihypertensive' },
                { label: 'Diabetes Medication (Insulin/Oral)', field: 'takes_diabetes_medicine' },
                { label: 'Inhaler', field: 'takes_inhaler' },
                { label: 'Blood Thinner', field: 'takes_blood_thinner' },
              ].map((item) => (
                <label key={item.field} className="flex items-center space-x-3 p-4 border border-slate-200 cursor-pointer hover:bg-slate-50 transition-colors">
                  <input
                    type="checkbox"
                    className="w-5 h-5 text-brand-600 border-slate-300 rounded-none focus:ring-brand-500"
                    checked={formData[item.field as keyof typeof formData] === 1.0}
                    onChange={handleCheckboxChange(item.field as keyof typeof formData)}
                  />
                  <span className="font-medium text-slate-700">{item.label}</span>
                </label>
              ))}
            </div>
          </div>
        );
    }
  };

  return (
    <div className="min-h-screen flex flex-col justify-center items-center p-6 bg-brand-50">
      <div className="w-full max-w-xl bg-white border border-brand-100 shadow-sm overflow-hidden">
        
        {/* Progress Bar */}
        <div className="flex bg-slate-100">
          {steps.map((step, idx) => (
            <div key={step.id} className={`flex-1 h-2 ${idx <= currentStep ? 'bg-brand-500' : 'bg-transparent'} transition-colors duration-300`} />
          ))}
        </div>

        <div className="p-8">
          <h2 className="text-xl font-medium text-slate-800 mb-6">{steps[currentStep].title}</h2>
          
          <AnimatePresence mode="wait">
            <motion.div
              key={currentStep}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.2 }}
            >
              {renderStepContent()}
            </motion.div>
          </AnimatePresence>

          <div className="mt-10 flex justify-end">
            <button
              onClick={handleNext}
              className="bg-brand-600 text-white font-medium py-3 px-6 hover:bg-brand-700 transition-colors flex items-center space-x-2"
            >
              <span>{currentStep === steps.length - 1 ? 'Complete Profile' : 'Next'}</span>
              {currentStep === steps.length - 1 ? <Check className="w-4 h-4" /> : <ArrowRight className="w-4 h-4" />}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
