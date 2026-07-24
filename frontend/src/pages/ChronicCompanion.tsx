import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '../api/client';
import { 
  Activity, Heart, Thermometer, Moon, Droplet, Dumbbell, 
  PlusCircle, BrainCircuit, AlertTriangle, ShieldCheck, User, Stethoscope, ChevronRight 
} from 'lucide-react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer 
} from 'recharts';
import { motion, AnimatePresence } from 'framer-motion';

type DailyLog = {
  id: number;
  log_date: string;
  fasting_glucose: number | null;
  post_meal_glucose: number | null;
  medication_taken: boolean;
  exercise_minutes: number;
  sleep_hours: number | null;
  water_ml: number | null;
  systolic_bp: number | null;
  diastolic_bp: number | null;
  diet_quality: string | null;
  weight_kg: number | null;
  notes: string | null;
};

type WeeklyReport = {
  id: number;
  start_date: string;
  end_date: string;
  avg_fasting_glucose: number | null;
  avg_post_meal_glucose: number | null;
  medication_adherence_pct: number;
  total_exercise_minutes: number;
  risk_level: string;
  patient_insight: string;
  actionable_nudges: string[];
  clinician_summary: string;
  created_at: string;
};

export const ChronicCompanion = () => {
  const navigate = useNavigate();

  // Logs state
  const [logs, setLogs] = useState<DailyLog[]>([]);
  const [report, setReport] = useState<WeeklyReport | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Form State
  const [formData, setFormData] = useState({
    fasting_glucose: '',
    post_meal_glucose: '',
    medication_taken: false,
    exercise_minutes: '30',
    sleep_hours: '7.5',
    systolic_bp: '',
    diastolic_bp: '',
  });

  const [activeTab, setActiveTab] = useState<'dashboard' | 'log'>('dashboard');

  useEffect(() => {
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    try {
      const res = await apiClient.get('/chronic/logs?days=7');
      // API returns newest first, so we reverse it for the chart
      setLogs(res.data.reverse());
    } catch (error) {
      console.error('Error fetching logs', error);
    }
  };

  const handleGenerateReport = async () => {
    setIsGenerating(true);
    try {
      const res = await apiClient.post('/chronic/report/generate');
      setReport(res.data);
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to generate report');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSubmitLog = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const payload = {
        fasting_glucose: formData.fasting_glucose ? parseFloat(formData.fasting_glucose) : null,
        post_meal_glucose: formData.post_meal_glucose ? parseFloat(formData.post_meal_glucose) : null,
        medication_taken: formData.medication_taken,
        exercise_minutes: parseInt(formData.exercise_minutes) || 0,
        sleep_hours: formData.sleep_hours ? parseFloat(formData.sleep_hours) : null,
        systolic_bp: formData.systolic_bp ? parseInt(formData.systolic_bp) : null,
        diastolic_bp: formData.diastolic_bp ? parseInt(formData.diastolic_bp) : null,
      };
      
      await apiClient.post('/chronic/log', payload);
      alert('Log saved successfully!');
      
      // Reset form and switch tab
      setFormData({
        fasting_glucose: '',
        post_meal_glucose: '',
        medication_taken: false,
        exercise_minutes: '30',
        sleep_hours: '7.5',
        systolic_bp: '',
        diastolic_bp: '',
      });
      setActiveTab('dashboard');
      fetchLogs();

    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to submit log');
    } finally {
      setIsSubmitting(false);
    }
  };

  const getRiskColor = (risk: string) => {
    if (risk === 'Low') return 'bg-emerald-100 text-emerald-800 border-emerald-200';
    if (risk === 'Medium') return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    if (risk === 'High') return 'bg-red-100 text-red-800 border-red-200';
    return 'bg-slate-100 text-slate-800 border-slate-200';
  };

  // Prepare chart data by mapping string dates to short weekday names
  const chartData = logs.map(l => ({
    ...l,
    name: new Date(l.log_date).toLocaleDateString('en-US', { weekday: 'short' }),
  }));

  return (
    <div className="min-h-screen bg-slate-50 font-sans p-6 md:p-10 overflow-y-auto">
      
      {/* Header */}
      <div className="max-w-6xl mx-auto mb-8">
        <div className="flex items-center gap-2 text-sm text-brand-600 mb-4 cursor-pointer hover:underline w-fit" onClick={() => navigate('/')}>
          <ChevronRight className="w-4 h-4 rotate-180" /> Back to Dashboard
        </div>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 flex items-center gap-3">
              <Activity className="w-8 h-8 text-brand-600" />
              Chronic Companion
            </h1>
            <p className="text-slate-500 mt-1">Track your vitals and receive AI-powered clinical insights.</p>
          </div>
          <div className="flex gap-2 bg-white p-1 rounded-xl shadow-sm border border-slate-200">
            <button 
              onClick={() => setActiveTab('dashboard')}
              className={`px-6 py-2 rounded-lg font-medium text-sm transition-all ${activeTab === 'dashboard' ? 'bg-brand-600 text-white shadow-md' : 'text-slate-600 hover:bg-slate-50'}`}
            >
              Dashboard
            </button>
            <button 
              onClick={() => setActiveTab('log')}
              className={`px-6 py-2 rounded-lg font-medium text-sm transition-all ${activeTab === 'log' ? 'bg-brand-600 text-white shadow-md' : 'text-slate-600 hover:bg-slate-50'}`}
            >
              Log Today
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto">
        <AnimatePresence mode="wait">
          
          {/* TAB: DASHBOARD */}
          {activeTab === 'dashboard' && (
            <motion.div 
              key="dashboard"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-6"
            >
              
              {/* Charts Row */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                
                {/* Glucose Chart */}
                <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="font-bold text-lg text-slate-800 flex items-center gap-2">
                      <Droplet className="w-5 h-5 text-blue-500" />
                      Blood Glucose (mg/dL)
                    </h3>
                  </div>
                  {chartData.length > 0 ? (
                    <div className="h-64 w-full">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                          <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#64748b' }} />
                          <YAxis axisLine={false} tickLine={false} tick={{ fill: '#64748b' }} domain={['dataMin - 10', 'dataMax + 10']} />
                          <Tooltip contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                          <Legend iconType="circle" />
                          <Line type="monotone" name="Fasting" dataKey="fasting_glucose" stroke="#3b82f6" strokeWidth={3} dot={{ r: 4, strokeWidth: 2 }} activeDot={{ r: 6 }} />
                          <Line type="monotone" name="Post-Meal" dataKey="post_meal_glucose" stroke="#0ea5e9" strokeWidth={3} dot={{ r: 4, strokeWidth: 2 }} strokeDasharray="5 5" />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  ) : (
                    <div className="h-64 flex flex-col items-center justify-center text-slate-400 bg-slate-50 rounded-xl border border-dashed border-slate-200">
                      <Activity className="w-8 h-8 mb-2 opacity-50" />
                      <p>No glucose logs found for the past 7 days.</p>
                      <button onClick={() => setActiveTab('log')} className="mt-3 text-brand-600 font-medium hover:underline">Log today's vitals</button>
                    </div>
                  )}
                </div>

                {/* Blood Pressure Chart */}
                <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="font-bold text-lg text-slate-800 flex items-center gap-2">
                      <Heart className="w-5 h-5 text-red-500" />
                      Blood Pressure (mmHg)
                    </h3>
                  </div>
                  {chartData.length > 0 ? (
                    <div className="h-64 w-full">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                          <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#64748b' }} />
                          <YAxis axisLine={false} tickLine={false} tick={{ fill: '#64748b' }} domain={['dataMin - 10', 'dataMax + 10']} />
                          <Tooltip contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                          <Legend iconType="circle" />
                          <Line type="monotone" name="Systolic" dataKey="systolic_bp" stroke="#ef4444" strokeWidth={3} dot={{ r: 4, strokeWidth: 2 }} />
                          <Line type="monotone" name="Diastolic" dataKey="diastolic_bp" stroke="#f43f5e" strokeWidth={3} dot={{ r: 4, strokeWidth: 2 }} strokeDasharray="5 5" />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  ) : (
                    <div className="h-64 flex flex-col items-center justify-center text-slate-400 bg-slate-50 rounded-xl border border-dashed border-slate-200">
                      <Heart className="w-8 h-8 mb-2 opacity-50" />
                      <p>No BP logs found for the past 7 days.</p>
                      <button onClick={() => setActiveTab('log')} className="mt-3 text-brand-600 font-medium hover:underline">Log today's vitals</button>
                    </div>
                  )}
                </div>

              </div>

              {/* AI Report Section */}
              <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-8">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
                  <div>
                    <h3 className="font-bold text-2xl text-slate-900 flex items-center gap-2">
                      <BrainCircuit className="w-7 h-7 text-purple-600" />
                      AI Health Report
                    </h3>
                    <p className="text-slate-500 mt-1">Generate a comprehensive weekly review using your latest vitals.</p>
                  </div>
                  <button 
                    onClick={handleGenerateReport}
                    disabled={isGenerating || logs.length === 0}
                    className="px-6 py-3 bg-purple-600 text-white rounded-xl font-bold hover:bg-purple-700 transition-colors shadow-md disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  >
                    {isGenerating ? (
                      <><Activity className="w-5 h-5 animate-spin" /> Analyzing Data...</>
                    ) : (
                      <><BrainCircuit className="w-5 h-5" /> Generate Insights</>
                    )}
                  </button>
                </div>

                {report && (
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-fade-in-up">
                    
                    {/* Left Col: Insights & Badges */}
                    <div className="lg:col-span-2 space-y-6">
                      <div className="bg-slate-50 rounded-2xl p-6 border border-slate-200">
                        <div className="flex items-center gap-3 mb-4">
                          <User className="w-6 h-6 text-brand-600" />
                          <h4 className="font-bold text-lg text-slate-800">Your Weekly Overview</h4>
                          <span className={`ml-auto px-4 py-1 rounded-full text-sm font-bold border ${getRiskColor(report.risk_level)}`}>
                            {report.risk_level} Risk
                          </span>
                        </div>
                        <p className="text-slate-700 leading-relaxed text-[15px]">{report.patient_insight}</p>
                      </div>

                      <div className="bg-purple-50 rounded-2xl p-6 border border-purple-100">
                        <h4 className="font-bold text-lg text-purple-900 flex items-center gap-2 mb-4">
                          <ShieldCheck className="w-6 h-6 text-purple-600" />
                          Actionable Nudges
                        </h4>
                        <ul className="space-y-3">
                          {report.actionable_nudges.map((nudge, idx) => (
                            <li key={idx} className="flex gap-3 text-purple-800 bg-white p-4 rounded-xl shadow-sm border border-purple-100/50">
                              <span className="flex-shrink-0 w-6 h-6 rounded-full bg-purple-100 text-purple-600 flex items-center justify-center text-sm font-bold">{idx + 1}</span>
                              <span className="text-[15px] font-medium">{nudge}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>

                    {/* Right Col: Clinician Summary */}
                    <div className="bg-brand-50 rounded-2xl p-6 border border-brand-100 flex flex-col">
                      <h4 className="font-bold text-lg text-brand-900 flex items-center gap-2 mb-4">
                        <Stethoscope className="w-6 h-6 text-brand-600" />
                        Clinician Summary
                      </h4>
                      <p className="text-brand-800 leading-relaxed text-[15px] italic border-l-4 border-brand-300 pl-4 mb-6 flex-1">
                        "{report.clinician_summary}"
                      </p>
                      
                      <div className="grid grid-cols-2 gap-4 mt-auto">
                        <div className="bg-white p-3 rounded-xl border border-brand-100">
                          <div className="text-xs text-brand-600 font-semibold mb-1 uppercase tracking-wider">Avg Fasting</div>
                          <div className="text-xl font-bold text-slate-800">{report.avg_fasting_glucose ? Math.round(report.avg_fasting_glucose) : '--'} <span className="text-sm font-normal text-slate-500">mg/dL</span></div>
                        </div>
                        <div className="bg-white p-3 rounded-xl border border-brand-100">
                          <div className="text-xs text-brand-600 font-semibold mb-1 uppercase tracking-wider">Adherence</div>
                          <div className="text-xl font-bold text-slate-800">{Math.round(report.medication_adherence_pct)}%</div>
                        </div>
                      </div>
                    </div>

                  </div>
                )}
              </div>
            </motion.div>
          )}

          {/* TAB: LOG TODAY */}
          {activeTab === 'log' && (
            <motion.div 
              key="log"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
            >
              <div className="max-w-2xl mx-auto bg-white rounded-2xl shadow-sm border border-slate-200 p-8">
                <div className="text-center mb-8">
                  <div className="w-16 h-16 bg-brand-100 text-brand-600 rounded-full flex items-center justify-center mx-auto mb-4">
                    <PlusCircle className="w-8 h-8" />
                  </div>
                  <h2 className="text-2xl font-bold text-slate-900">Log Today's Vitals</h2>
                  <p className="text-slate-500 mt-2">Track your metrics to feed the AI health engine.</p>
                </div>

                <form onSubmit={handleSubmitLog} className="space-y-6">
                  
                  {/* Glucose Row */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-semibold text-slate-700 mb-2 flex items-center gap-2">
                        <Droplet className="w-4 h-4 text-blue-500" /> Fasting Glucose
                      </label>
                      <div className="relative">
                        <input 
                          type="number" step="0.1"
                          className="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 pr-16 focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-shadow outline-none font-medium"
                          placeholder="e.g. 105"
                          value={formData.fasting_glucose}
                          onChange={(e) => setFormData({...formData, fasting_glucose: e.target.value})}
                        />
                        <span className="absolute right-4 top-3 text-sm text-slate-400 font-medium">mg/dL</span>
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-slate-700 mb-2">
                        Post-Meal Glucose
                      </label>
                      <div className="relative">
                        <input 
                          type="number" step="0.1"
                          className="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 pr-16 focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-shadow outline-none font-medium"
                          placeholder="e.g. 140"
                          value={formData.post_meal_glucose}
                          onChange={(e) => setFormData({...formData, post_meal_glucose: e.target.value})}
                        />
                        <span className="absolute right-4 top-3 text-sm text-slate-400 font-medium">mg/dL</span>
                      </div>
                    </div>
                  </div>

                  {/* BP Row */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-semibold text-slate-700 mb-2 flex items-center gap-2">
                        <Heart className="w-4 h-4 text-red-500" /> Systolic BP
                      </label>
                      <div className="relative">
                        <input 
                          type="number"
                          className="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-shadow outline-none font-medium"
                          placeholder="e.g. 120"
                          value={formData.systolic_bp}
                          onChange={(e) => setFormData({...formData, systolic_bp: e.target.value})}
                        />
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-slate-700 mb-2">
                        Diastolic BP
                      </label>
                      <div className="relative">
                        <input 
                          type="number"
                          className="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-shadow outline-none font-medium"
                          placeholder="e.g. 80"
                          value={formData.diastolic_bp}
                          onChange={(e) => setFormData({...formData, diastolic_bp: e.target.value})}
                        />
                      </div>
                    </div>
                  </div>

                  {/* Lifestyle Row */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-semibold text-slate-700 mb-2 flex items-center gap-2">
                        <Dumbbell className="w-4 h-4 text-orange-500" /> Exercise
                      </label>
                      <div className="relative">
                        <input 
                          type="number"
                          className="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 pr-16 focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-shadow outline-none font-medium"
                          value={formData.exercise_minutes}
                          onChange={(e) => setFormData({...formData, exercise_minutes: e.target.value})}
                        />
                        <span className="absolute right-4 top-3 text-sm text-slate-400 font-medium">min</span>
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-slate-700 mb-2 flex items-center gap-2">
                        <Moon className="w-4 h-4 text-indigo-500" /> Sleep
                      </label>
                      <div className="relative">
                        <input 
                          type="number" step="0.5"
                          className="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 pr-16 focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-shadow outline-none font-medium"
                          value={formData.sleep_hours}
                          onChange={(e) => setFormData({...formData, sleep_hours: e.target.value})}
                        />
                        <span className="absolute right-4 top-3 text-sm text-slate-400 font-medium">hrs</span>
                      </div>
                    </div>
                  </div>

                  {/* Medication Toggle */}
                  <div className="bg-brand-50 border border-brand-100 rounded-xl p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 mt-6">
                    <div>
                      <h4 className="font-bold text-brand-900">Medication Adherence</h4>
                      <p className="text-sm text-brand-700">Did you take all prescribed medications today?</p>
                    </div>
                    <button
                      type="button"
                      onClick={() => setFormData({...formData, medication_taken: !formData.medication_taken})}
                      className={`relative inline-flex h-8 w-14 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-brand-500 focus:ring-offset-2 ${formData.medication_taken ? 'bg-brand-600' : 'bg-slate-300'}`}
                    >
                      <span className={`pointer-events-none inline-block h-7 w-7 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${formData.medication_taken ? 'translate-x-6' : 'translate-x-0'}`} />
                    </button>
                  </div>

                  <button 
                    type="submit"
                    disabled={isSubmitting}
                    className="w-full mt-8 bg-slate-900 text-white font-bold text-lg py-4 rounded-xl shadow-lg hover:bg-slate-800 transition-all transform hover:scale-[1.01] active:scale-[0.99] disabled:opacity-70 flex items-center justify-center gap-2"
                  >
                    {isSubmitting ? (
                      <><Activity className="w-5 h-5 animate-spin" /> Saving...</>
                    ) : (
                      'Save Today\'s Vitals'
                    )}
                  </button>

                </form>
              </div>
            </motion.div>
          )}

        </AnimatePresence>
      </div>
    </div>
  );
};
