import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { api } from '../utils/api';
import { ArrowRight, Settings, Utensils, AlertCircle } from 'lucide-react';

export default function OnboardingPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  
  const [dietType, setDietType] = useState('Standard');
  const [targetCalories, setTargetCalories] = useState(2000);
  const [targetProtein, setTargetProtein] = useState(120);
  const [targetCarbs, setTargetCarbs] = useState(250);
  const [targetFat, setTargetFat] = useState(65);
  const [prefGenDay, setPrefGenDay] = useState('Sunday');
  
  const [saving, setSaving] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;
    
    setSaving(true);
    setErrorMsg('');

    try {
      const prefData = {
        diet_type: dietType,
        target_calories: Number(targetCalories),
        target_protein_g: Number(targetProtein),
        target_carbs_g: Number(targetCarbs),
        target_fat_g: Number(targetFat),
        preferred_generation_day: prefGenDay
      };
      
      const createRes = await api.post(`/users/${user.id}/preferences`, prefData);
      
      if (!createRes.success) {
          // Sometimes it might already exist if they double clicked, try PUT instead
          const putRes = await api.put(`/users/${user.id}/preferences`, prefData);
          if (!putRes.success) {
             throw new Error(createRes.message || putRes.message || 'Gagal menyimpan pengaturan');
          }
      }

      // Success!
      navigate('/dashboard');
    } catch (error) {
      setErrorMsg(error instanceof Error ? error.message : 'Terjadi kesalahan saat menyimpan pengaturan preferensi.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-[90vh] py-12 animate-in fade-in duration-500">
      <div className="w-full max-w-2xl bg-white p-8 md:p-12 rounded-3xl shadow-2xl shadow-slate-200/50 border border-slate-100">
        
        <div className="flex flex-col items-center mb-10 text-center">
          <div className="w-20 h-20 bg-emerald-100 text-emerald-600 rounded-[2rem] flex items-center justify-center mb-6 shadow-inner">
            <Utensils className="w-10 h-10" />
          </div>
          <h1 className="text-3xl md:text-4xl font-extrabold text-slate-900 tracking-tight mb-3">Selamat Datang di NutriGuard!</h1>
          <p className="text-slate-500 text-lg max-w-md">Lengkapi pengaturan profil gizi Anda untuk mendapatkan rekomendasi makanan terbaik.</p>
        </div>

        {errorMsg && (
          <div className="mb-8 p-4 bg-rose-50 rounded-xl flex items-start gap-3 border border-rose-100 animate-in slide-in-from-top-2">
            <AlertCircle className="w-5 h-5 text-rose-500 shrink-0 mt-0.5" />
            <p className="text-sm font-medium text-rose-700">{errorMsg}</p>
          </div>
        )}

        <form onSubmit={handleSave} className="space-y-6">
           <div className="flex items-center gap-3 mb-4 pb-4 border-b border-slate-100">
            <div className="p-2 bg-amber-50 text-amber-600 rounded-lg">
              <Settings className="w-5 h-5" />
            </div>
            <h2 className="text-lg font-bold text-slate-800">Target Makronutrisi</h2>
          </div>

          <div className="grid md:grid-cols-2 gap-5">
            <div className="md:col-span-2">
               <label className="block text-sm font-semibold text-slate-700 mb-2">Tipe Diet</label>
               <select 
                  value={dietType}
                  onChange={(e) => setDietType(e.target.value)}
                  className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 font-medium text-slate-800 transition-shadow"
                >
                  <option value="Standard">Standar</option>
                  <option value="Keto">Keto</option>
                  <option value="Vegetarian">Vegetarian</option>
                  <option value="High Protein">Tinggi Protein</option>
               </select>
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-semibold text-slate-700 mb-2">Target Kalori Harian (kcal)</label>
              <input
                type="number"
                value={targetCalories}
                onChange={(e) => setTargetCalories(Number(e.target.value))}
                className="w-full px-4 py-4 bg-emerald-50/50 border border-emerald-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 text-emerald-700 font-bold text-xl transition-shadow"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">Protein (g)</label>
              <input
                type="number"
                value={targetProtein}
                onChange={(e) => setTargetProtein(Number(e.target.value))}
                className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 font-medium text-slate-800 transition-shadow"
              />
            </div>
             <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">Karbohidrat (g)</label>
              <input
                type="number"
                value={targetCarbs}
                onChange={(e) => setTargetCarbs(Number(e.target.value))}
                className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 font-medium text-slate-800 transition-shadow"
              />
            </div>
             <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">Lemak (g)</label>
              <input
                type="number"
                value={targetFat}
                onChange={(e) => setTargetFat(Number(e.target.value))}
                className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 font-medium text-slate-800 transition-shadow"
              />
            </div>
             <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">Hari Perencanaan Mingguan</label>
              <select 
                  value={prefGenDay}
                  onChange={(e) => setPrefGenDay(e.target.value)}
                  className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 font-medium text-slate-800 transition-shadow"
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
              className="w-full flex items-center justify-center gap-2 py-4 px-4 mt-8 border border-transparent rounded-xl shadow-md text-base font-bold text-white bg-emerald-600 hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 disabled:opacity-70 transition-all hover:scale-[1.01] active:scale-[0.99]"
            >
              {saving ? 'Menyimpan...' : 'Mulai Sekarang'}
              {!saving && <ArrowRight className="w-5 h-5" />}
          </button>
        </form>
      </div>
    </div>
  );
}
