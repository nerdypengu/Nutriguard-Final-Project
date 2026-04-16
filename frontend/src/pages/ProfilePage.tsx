import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../utils/api';
import { Save, User, Settings, AlertCircle, CheckCircle2, ExternalLink } from 'lucide-react';

export default function ProfilePage() {
  const { user, login } = useAuth();
  
  // Preferences state
  const [dietType, setDietType] = useState('Standard');
  const [targetCalories, setTargetCalories] = useState(2000);
  const [targetProtein, setTargetProtein] = useState(120);
  const [targetCarbs, setTargetCarbs] = useState(250);
  const [targetFat, setTargetFat] = useState(65);
  const [prefGenDay, setPrefGenDay] = useState('Sunday');
  
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  useEffect(() => {
    if (!user) return;
    
    // Fetch preferences
    api.get(`/users/${user.id}/preferences`)
      .then((res) => {
        if (res.success && res.data) {
          setDietType(res.data.diet_type || 'Standard');
          setTargetCalories(res.data.target_calories || 2000);
          setTargetProtein(res.data.target_protein_g || 120);
          setTargetCarbs(res.data.target_carbs_g || 250);
          setTargetFat(res.data.target_fat_g || 65);
          setPrefGenDay(res.data.preferred_generation_day || 'Sunday');
        }
      })
      .catch((err) => {
        console.error('Failed to load preferences', err);
        // If 404, it means preferences not created yet. That's fine.
      })
      .finally(() => {
        setLoading(false);
      });
  }, [user]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;
    
    setSaving(true);
    setMessage({ type: '', text: '' });

    try {
      // 1. Update Preferences
      const prefData = {
        diet_type: dietType,
        target_calories: Number(targetCalories),
        target_protein_g: Number(targetProtein),
        target_carbs_g: Number(targetCarbs),
        target_fat_g: Number(targetFat),
        preferred_generation_day: prefGenDay
      };
      
      const prefRes = await api.put(`/users/${user.id}/preferences`, prefData);
      if (!prefRes.success) {
         // If it fails (e.g. preferences not found), try creating
         const createRes = await api.post(`/users/${user.id}/preferences`, prefData);
         if (!createRes.success) throw new Error(createRes.message || 'Gagal membuat pengaturan baru');
      }

      setMessage({ type: 'success', text: 'Pengaturan berhasil disimpan!' });
    } catch (error: any) {
      setMessage({ type: 'error', text: error.message || 'Terjadi kesalahan saat menyimpan.' });
    } finally {
      setSaving(false);
      setTimeout(() => setMessage({ type: '', text: '' }), 5000);
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-slate-500">Memuat profil...</div>;
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in duration-500">
      <div>
        <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Pengaturan Profil</h1>
        <p className="text-slate-500 mt-1">Atur integrasi dan target gizi harian Anda.</p>
      </div>

      {message.text && (
        <div className={`p-4 rounded-xl flex items-center gap-3 animate-in fade-in ${message.type === 'success' ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-rose-50 text-rose-800 border border-rose-200'}`}>
          {message.type === 'success' ? <CheckCircle2 className="w-5 h-5 text-emerald-500" /> : <AlertCircle className="w-5 h-5 text-rose-500" />}
          <p className="font-medium">{message.text}</p>
        </div>
      )}

      <form onSubmit={handleSave} className="grid md:grid-cols-2 gap-8">
        {/* Preferences Card */}
        <div className="bg-white rounded-3xl p-6 shadow-sm border border-slate-100 space-y-5">
           <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-amber-50 text-amber-600 rounded-lg">
              <Settings className="w-6 h-6" />
            </div>
            <h2 className="text-xl font-bold text-slate-800">Target Makronutrisi</h2>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2">
               <label className="block text-sm font-semibold text-slate-700 mb-2">Tipe Diet</label>
               <select 
                  value={dietType}
                  onChange={(e) => setDietType(e.target.value)}
                  className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 font-medium text-slate-800"
                >
                  <option value="Standard">Standar</option>
                  <option value="Keto">Keto</option>
                  <option value="Vegetarian">Vegetarian</option>
                  <option value="High Protein">Tinggi Protein</option>
               </select>
            </div>
            <div className="col-span-2">
              <label className="block text-sm font-semibold text-slate-700 mb-2">Target Kalori Harian (kcal)</label>
              <input
                type="number"
                value={targetCalories}
                onChange={(e) => setTargetCalories(Number(e.target.value))}
                className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 font-bold text-emerald-600 text-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">Protein (g)</label>
              <input
                type="number"
                value={targetProtein}
                onChange={(e) => setTargetProtein(Number(e.target.value))}
                className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 font-medium text-slate-800"
              />
            </div>
             <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">Karbohidrat (g)</label>
              <input
                type="number"
                value={targetCarbs}
                onChange={(e) => setTargetCarbs(Number(e.target.value))}
                className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 font-medium text-slate-800"
              />
            </div>
             <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">Lemak (g)</label>
              <input
                type="number"
                value={targetFat}
                onChange={(e) => setTargetFat(Number(e.target.value))}
                className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 font-medium text-slate-800"
              />
            </div>
             <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">Hari Rencana</label>
              <select 
                  value={prefGenDay}
                  onChange={(e) => setPrefGenDay(e.target.value)}
                  className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 font-medium text-slate-800"
                >
                  <option value="Monday">Senin</option>
                  <option value="Saturday">Sabtu</option>
                  <option value="Sunday">Minggu</option>
               </select>
            </div>
          </div>

          <button
              type="submit"
              disabled={saving}
              className="w-full flex items-center justify-center gap-2 py-4 px-4 mt-6 border border-transparent rounded-xl shadow-sm text-base font-bold text-white bg-emerald-600 hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 disabled:opacity-70 transition-all"
            >
              <Save className="w-5 h-5" />
              {saving ? 'Menyimpan...' : 'Simpan Pengaturan'}
          </button>
        </div>
      </form>
    </div>
  );
}
