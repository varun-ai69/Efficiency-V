import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { apiClient } from '../api/client';
import { Menu, X, Send, Bot, User, Activity, AlertCircle, Clock, Home } from 'lucide-react';

type Message = {
  id: string;
  sender: 'bot' | 'user';
  text: string;
  isCard?: boolean; // Used for rendering the final prediction card
  prediction?: any;
};

type HistoryItem = {
  id: int;
  original_text: string;
  status: string;
  created_at: string;
};

export const TriageChat = () => {
  const navigate = useNavigate();
  
  // State
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  // Session State
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [status, setStatus] = useState<'idle' | 'in_progress' | 'completed'>('idle');
  const [nextFeature, setNextFeature] = useState<string | null>(null);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initial mount
  useEffect(() => {
    fetchHistory();
    // Welcome message
    setMessages([
      { id: 'welcome', sender: 'bot', text: 'Hello! I am your AI Symptom Checker. I will ask you a few questions to understand your condition and provide a rapid ML-powered triage assessment. What seems to be the problem today?' }
    ]);
  }, []);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const fetchHistory = async () => {
    try {
      const res = await apiClient.get('/triage/history');
      setHistory(res.data);
    } catch (err) {
      console.error("Failed to load history", err);
    }
  };

  const startTriage = async (complaint: string) => {
    try {
      const res = await apiClient.post('/triage/start', { complaint });
      setSessionId(res.data.session_id);
      setStatus(res.data.status);
      setNextFeature(res.data.next_question_feature);
      
      setMessages(prev => [...prev, { id: Date.now().toString(), sender: 'bot', text: res.data.message }]);
      fetchHistory(); // Refresh history to show the new chat
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, { id: Date.now().toString(), sender: 'bot', text: 'Sorry, our systems encountered an error starting the triage.' }]);
    }
  };

  const answerTriage = async (value: string) => {
    if (!sessionId || !nextFeature) return;
    try {
      const res = await apiClient.post(`/triage/${sessionId}/answer`, {
        feature_name: nextFeature,
        feature_value: value
      });
      
      setStatus(res.data.status);
      setNextFeature(res.data.next_question_feature);
      
      if (res.data.status === 'completed') {
        setMessages(prev => [...prev, { id: Date.now().toString(), sender: 'bot', text: 'Thank you. I am now analyzing your symptoms using our ML triage engine...' }]);
        await runPrediction(res.data.session_id);
      } else {
        setMessages(prev => [...prev, { id: Date.now().toString(), sender: 'bot', text: res.data.message }]);
      }
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, { id: Date.now().toString(), sender: 'bot', text: 'Sorry, I had trouble processing that.' }]);
    }
  };

  const runPrediction = async (sId: number) => {
    try {
      // Predict route expects POST /predict/{session_id} with NO body
      const predRes = await apiClient.post(`/predict/${sId}`);
      
      // Render Card
      setMessages(prev => [...prev, { 
        id: Date.now().toString(), 
        sender: 'bot', 
        text: '', 
        isCard: true, 
        prediction: predRes.data 
      }]);
      
      setStatus('completed');
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, { id: Date.now().toString(), sender: 'bot', text: 'Error generating final prediction. Please try again.' }]);
    }
  };

  const handleSend = async (textOverride?: string) => {
    const text = textOverride !== undefined ? textOverride : inputValue.trim();
    if (!text || isLoading) return;
    setInputValue('');
    
    // Add user message
    setMessages(prev => [...prev, { id: Date.now().toString(), sender: 'user', text }]);
    setIsLoading(true);
    
    if (status === 'idle') {
      await startTriage(text);
    } else if (status === 'in_progress') {
      await answerTriage(text);
    }
    
    setIsLoading(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Render Alert Card based on prediction class
  const getAlertColor = (predClass: any) => {
    const classStr = String(predClass || '');
    if (classStr.includes('Emergency') || classStr.includes('Resuscitation')) return 'bg-red-50 border-red-200 text-red-900';
    if (classStr.includes('Urgent')) return 'bg-orange-50 border-orange-200 text-orange-900';
    return 'bg-brand-50 border-brand-200 text-brand-900';
  };

  const renderInputArea = () => {
    if (status === 'completed') {
      return (
        <div className="p-4 bg-slate-50 border-t border-slate-200 text-center text-sm text-slate-500 flex flex-col items-center gap-3">
          <p>Triage session completed.</p>
          <button 
            onClick={() => {
              setSessionId(null);
              setStatus('idle');
              setNextFeature(null);
              setMessages([{ id: Date.now().toString(), sender: 'bot', text: 'Hello! I am your AI Symptom Checker. I will ask you a few questions to understand your condition and provide a rapid ML-powered triage assessment. What seems to be the problem today?' }]);
            }}
            className="px-6 py-2 bg-brand-600 text-white rounded font-medium hover:bg-brand-700 transition-colors shadow-sm"
          >
            Start New Assessment
          </button>
        </div>
      );
    }

    // Dynamic UI — all template features are explicitly mapped. No free-text during session.
    if (status === 'in_progress' && nextFeature) {

      // ─── Sliders ──────────────────────────────────────────────────────────
      if (['symptom_severity', 'pain_score'].includes(nextFeature)) {
        const sliderVal = inputValue || '5';
        return (
          <div className="p-6 bg-white border-t border-slate-200 flex flex-col items-center gap-4">
            <div className="flex items-center gap-3">
              <span className="text-sm font-medium text-slate-700">Pain / Severity:</span>
              <span className="text-2xl font-bold text-brand-600">{sliderVal} / 10</span>
            </div>
            <input type="range" min="1" max="10" step="1"
              className="w-full max-w-xs accent-brand-600 h-2 cursor-pointer"
              value={sliderVal}
              onChange={(e) => setInputValue(e.target.value)}
            />
            <div className="flex justify-between w-full max-w-xs text-xs text-slate-400 px-1">
              <span>Mild (1)</span><span>Severe (10)</span>
            </div>
            <button onClick={() => handleSend(sliderVal)}
              className="px-8 py-2 bg-brand-600 text-white font-medium hover:bg-brand-700 transition-colors shadow-sm">
              Submit
            </button>
          </div>
        );
      }

      // ─── Duration (number of days) ─────────────────────────────────────────
      if (nextFeature === 'symptom_duration') {
        return (
          <div className="p-4 bg-white border-t border-slate-200 flex flex-col items-center gap-4">
            <span className="text-sm font-medium text-slate-700">How many days have you had this symptom?</span>
            <div className="flex gap-2">
              <input type="number" min="0" max="365" step="1"
                className="w-28 border border-slate-300 p-3 text-center text-lg font-semibold focus:outline-none focus:ring-1 focus:ring-brand-500"
                placeholder="0"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
              />
              <button onClick={() => handleSend(inputValue || '1')}
                className="px-6 py-2 bg-brand-600 text-white font-medium hover:bg-brand-700 transition-colors shadow-sm disabled:opacity-50">
                Submit
              </button>
            </div>
            <div className="flex gap-2 flex-wrap justify-center">
              {['1', '2', '3', '7', '14', '30'].map(d => (
                <button key={d} onClick={() => handleSend(d)}
                  className="px-4 py-1.5 border border-slate-300 text-sm text-slate-600 hover:border-brand-600 hover:text-brand-600 transition-colors">
                  {d} {d === '1' ? 'day' : 'days'}
                </button>
              ))}
            </div>
          </div>
        );
      }

      // ─── Temperature (°F) ─────────────────────────────────────────────────
      if (nextFeature === 'body_temperature') {
        return (
          <div className="p-4 bg-white border-t border-slate-200 flex flex-col items-center gap-4">
            <span className="text-sm font-medium text-slate-700">What is your temperature (°F)?</span>
            <div className="flex gap-2">
              <input type="number" min="95" max="107" step="0.1"
                className="w-32 border border-slate-300 p-3 text-center text-lg font-semibold focus:outline-none focus:ring-1 focus:ring-brand-500"
                placeholder="98.6"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
              />
              <button onClick={() => handleSend(inputValue || '98.6')}
                className="px-6 py-2 bg-brand-600 text-white font-medium hover:bg-brand-700 transition-colors shadow-sm">
                Submit
              </button>
            </div>
            <div className="flex gap-2 flex-wrap justify-center">
              {[{label:'Normal (98.6)', val:'98.6'}, {label:'Low Fever (100)', val:'100'}, {label:'Fever (102)', val:'102'}, {label:'High Fever (104)', val:'104'}].map(opt => (
                <button key={opt.val} onClick={() => handleSend(opt.val)}
                  className="px-3 py-1.5 border border-slate-300 text-sm text-slate-600 hover:border-brand-600 hover:text-brand-600 transition-colors">
                  {opt.label}
                </button>
              ))}
            </div>
          </div>
        );
      }

      // ─── Onset ────────────────────────────────────────────────────────────
      if (nextFeature === 'symptom_onset') {
        return (
          <div className="p-4 bg-white border-t border-slate-200 flex flex-col items-center gap-3">
            <span className="text-sm font-medium text-slate-500 mb-1">How did it start?</span>
            <div className="flex gap-3 flex-wrap justify-center">
              {[
                {label:'Gradually', val:'Gradual'},
                {label:'Acutely', val:'Acute'},
                {label:'Suddenly', val:'Sudden'},
              ].map(opt => (
                <button key={opt.val} onClick={() => handleSend(opt.val)}
                  className="px-5 py-3 border border-brand-600 text-brand-600 font-medium hover:bg-brand-50 transition-colors shadow-sm text-sm">
                  {opt.label}
                </button>
              ))}
            </div>
          </div>
        );
      }

      // ─── Progression ──────────────────────────────────────────────────────
      if (nextFeature === 'progression') {
        return (
          <div className="p-4 bg-white border-t border-slate-200 flex flex-col items-center gap-3">
            <span className="text-sm font-medium text-slate-500 mb-1">How has it changed?</span>
            <div className="flex gap-3 flex-wrap justify-center">
              {[
                {label:'Getting Better', val:'Better'},
                {label:'Staying the Same', val:'Same'},
                {label:'Getting Worse', val:'Worse'},
              ].map(opt => (
                <button key={opt.val} onClick={() => handleSend(opt.val)}
                  className="px-5 py-3 border border-brand-600 text-brand-600 font-medium hover:bg-brand-50 transition-colors shadow-sm text-sm">
                  {opt.label}
                </button>
              ))}
            </div>
          </div>
        );
      }

      // ─── Pain Type ────────────────────────────────────────────────────────
      if (nextFeature === 'pain_type') {
        return (
          <div className="p-4 bg-white border-t border-slate-200 flex flex-col items-center gap-3">
            <span className="text-sm font-medium text-slate-500 mb-1">Describe the pain:</span>
            <div className="flex gap-3 flex-wrap justify-center">
              {['Sharp', 'Burning', 'Crushing', 'Stabbing', 'Pressure', 'Dull'].map(opt => (
                <button key={opt} onClick={() => handleSend(opt)}
                  className="px-5 py-2 border border-brand-600 text-brand-600 font-medium hover:bg-brand-50 transition-colors shadow-sm text-sm">
                  {opt}
                </button>
              ))}
            </div>
          </div>
        );
      }

      // ─── Yes / No fallback for ALL remaining binary features ──────────────
      // This covers every binary feature from every template YAML:
      // cardiovascular, respiratory, neuro, GI, GU, trauma, etc.
      const yesNoFeatures = new Set([
        // Cardiovascular
        'radiating_pain','chest_tightness','palpitations','leg_swelling',
        'shortness_of_breath','severe_chest_pain','one_sided_swelling','previous_dvt',
        'takes_cardiovascular_meds','heart_disease',
        // Respiratory
        'persistent_cough','bloody_cough','wheezing','severe_shortness_of_breath',
        'breathing_difficulty','cough','asthma','copd','takes_inhaler','smoker',
        'recent_infection',
        // Neurological
        'neck_stiffness','light_sensitivity','vision_changes','confusion',
        'slurred_speech','facial_droop','weakness_one_side','weakness_both_legs',
        'loss_of_consciousness','post_ictal_confusion','room_spinning','dizziness',
        'seizure_active','recent_head_injury','takes_epilepsy_meds','alcohol_withdrawal',
        'fast_positive','previous_stroke','stroke_symptoms','syncope',
        // GI
        'abdominal_tenderness','diarrhea','vomiting','bloody_vomit','bloody_stool',
        'inability_to_keep_fluids','rigid_abdomen','food_poisoning_suspicion',
        'alcohol_use','recent_surgery',
        // GU
        'burning_urination','urinary_frequency','flank_pain','severe_flank_pain',
        'unable_to_urinate','recurrent_uti','uti',
        // General symptoms
        'fever_present','fever','body_aches','fatigue','recent_travel',
        'covid_contact','tick_bite','animal_bite',
        // Emergency flags
        'unconscious','unable_to_speak','severe_bleeding','cyanosis',
        'unable_to_breathe','seizure',
        // Trauma
        'recent_injury','head_injury','bleeding','osteoporosis','head_trauma_with_vomiting',
        // Skin
        'rash','itching','spreading_rapidly','new_medication','facial_swelling',
        'purple_non_blanching_spots','throat_tightness','tongue_swelling','throat_closing',
        // Misc
        'intermittent','relieved_by_rest','long_travel','sudden_shortness_of_breath',
        'sudden_onset','sudden_onset_exercise','leg_weakness','numbness','previous_back_pain',
        'arthritis','loss_of_bladder_control','fever_with_back_pain','dehydration',
        'anemia','hypertension','diabetes','known_allergy','epipen_available',
        'new_exposure','anxiety','caffeine_intake','takes_blood_thinner',
        'takes_antihypertensive','takes_diabetes_medicine','difficulty_swallowing',
        'swollen_neck','recent_covid_contact','unable_to_swallow_saliva',
        'pregnancy_status','high_fever','severe_dehydration',
        'chest_pain','previous_migraine','chest_pain','recent_dvt',
        'heart_failure','previous_angina','shortness_of_breath_at_rest',
      ]);

      if (yesNoFeatures.has(nextFeature)) {
        return (
          <div className="p-6 bg-white border-t border-slate-200 flex justify-center gap-6">
            <button onClick={() => handleSend('Yes')}
              className="px-10 py-3 bg-brand-600 text-white text-base font-semibold hover:bg-brand-700 transition-colors shadow-sm">
              Yes
            </button>
            <button onClick={() => handleSend('No')}
              className="px-10 py-3 bg-slate-100 text-slate-800 text-base font-semibold hover:bg-slate-200 border border-slate-300 transition-colors shadow-sm">
              No
            </button>
          </div>
        );
      }

      // ─── Ultimate fallback — Yes/No for anything not explicitly matched ──
      // (catches any future template features we haven't explicitly listed)
      return (
        <div className="p-6 bg-white border-t border-slate-200 flex justify-center gap-6">
          <button onClick={() => handleSend('Yes')}
            className="px-10 py-3 bg-brand-600 text-white text-base font-semibold hover:bg-brand-700 transition-colors shadow-sm">
            Yes
          </button>
          <button onClick={() => handleSend('No')}
            className="px-10 py-3 bg-slate-100 text-slate-800 text-base font-semibold hover:bg-slate-200 border border-slate-300 transition-colors shadow-sm">
            No
          </button>
        </div>
      );
    }

    // ─── Initial text box — only shown before the session starts ────────────
    return (
      <div className="p-4 bg-white border-t border-slate-200">
        <div className="max-w-4xl mx-auto flex items-end gap-2">
          <textarea
            className="flex-1 border border-slate-300 p-3 max-h-32 min-h-[50px] resize-none focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 text-[15px]"
            placeholder="Describe your main symptoms..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
            rows={1}
          />
          <button
            onClick={() => handleSend()}
            disabled={!inputValue.trim() || isLoading}
            className="h-[50px] px-6 bg-brand-600 text-white font-medium hover:bg-brand-700 disabled:opacity-50 transition-colors flex items-center justify-center shadow-sm"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="flex h-screen bg-brand-50 font-sans text-slate-900 overflow-hidden">
      
      {/* Sidebar Navigation */}
      <AnimatePresence>
        {(isSidebarOpen || window.innerWidth >= 1024) && (
          <motion.div
            initial={{ x: -300 }}
            animate={{ x: 0 }}
            exit={{ x: -300 }}
            transition={{ type: 'spring', bounce: 0, duration: 0.4 }}
            className="fixed lg:relative z-20 w-64 h-full bg-white border-r border-slate-200 flex flex-col shadow-xl lg:shadow-none"
          >
            <div className="p-4 border-b border-slate-100 flex justify-between items-center bg-brand-600 text-white">
              <span className="font-medium tracking-wide flex items-center gap-2">
                <Activity className="w-5 h-5" /> Past Chats
              </span>
              <button className="lg:hidden" onClick={() => setIsSidebarOpen(false)}>
                <X className="w-5 h-5 text-white" />
              </button>
            </div>
            
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {history.length === 0 ? (
                <p className="text-sm text-slate-500 italic text-center mt-4">No past sessions.</p>
              ) : (
                history.map(item => (
                  <div key={item.id} className="p-3 border border-slate-100 hover:bg-slate-50 cursor-pointer transition-colors group">
                    <p className="text-sm font-medium text-slate-800 line-clamp-1 group-hover:text-brand-600 transition-colors">{item.original_text}</p>
                    <div className="flex items-center gap-1 mt-2 text-xs text-slate-400">
                      <Clock className="w-3 h-3" />
                      <span>{new Date(item.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-w-0 bg-white">
        {/* Header */}
        <header className="h-16 border-b border-slate-200 flex items-center justify-between px-4 sm:px-6 flex-shrink-0">
          <div className="flex items-center gap-3">
            <button className="lg:hidden text-slate-500 hover:text-brand-600" onClick={() => setIsSidebarOpen(true)}>
              <Menu className="w-6 h-6" />
            </button>
            <h1 className="text-lg font-semibold text-slate-800">Symptom Checker</h1>
          </div>
          <button onClick={() => navigate('/')} className="text-sm font-medium text-slate-500 hover:text-brand-600 flex items-center gap-2">
            <Home className="w-4 h-4" /> Home
          </button>
        </header>

        {/* Chat Stream */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6 bg-slate-50">
          {messages.map((msg) => (
            <div key={msg.id} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
              
              <div className={`flex max-w-[85%] sm:max-w-[70%] gap-3 ${msg.sender === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                {/* Avatar */}
                <div className="flex-shrink-0">
                  {msg.sender === 'bot' ? (
                    <div className="w-8 h-8 bg-brand-100 flex items-center justify-center">
                      <Bot className="w-5 h-5 text-brand-600" />
                    </div>
                  ) : (
                    <div className="w-8 h-8 bg-slate-800 flex items-center justify-center">
                      <User className="w-5 h-5 text-white" />
                    </div>
                  )}
                </div>

                {/* Message Bubble */}
                {msg.isCard && msg.prediction ? (
                  // Final Prediction Card
                  <div className={`p-5 border ${getAlertColor(msg.prediction.label)}`}>
                    <div className="flex items-center gap-2 mb-3">
                      <AlertCircle className="w-5 h-5" />
                      <h3 className="font-semibold text-lg">{msg.prediction.label}</h3>
                    </div>
                    <p className="text-sm mb-4 leading-relaxed font-medium">Confidence: {(msg.prediction.confidence * 100).toFixed(1)}%</p>
                    <div className="prose prose-sm prose-slate bg-white p-4 border border-inherit shadow-sm">
                      <p className="whitespace-pre-wrap">{msg.prediction.explanation}</p>
                    </div>
                  </div>
                ) : (
                  // Normal Text Bubble
                  <div className={`px-4 py-3 text-[15px] leading-relaxed shadow-sm ${
                    msg.sender === 'user' 
                      ? 'bg-brand-600 text-white border border-brand-700' 
                      : 'bg-white text-slate-800 border border-slate-200'
                  }`}>
                    {msg.text}
                  </div>
                )}
              </div>

            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="flex gap-3">
                <div className="w-8 h-8 bg-brand-100 flex items-center justify-center">
                  <Bot className="w-5 h-5 text-brand-600" />
                </div>
                <div className="px-4 py-3 bg-white border border-slate-200 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 bg-brand-400 rounded-full animate-bounce"></span>
                  <span className="w-1.5 h-1.5 bg-brand-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></span>
                  <span className="w-1.5 h-1.5 bg-brand-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        {renderInputArea()}
      </div>

    </div>
  );
};
