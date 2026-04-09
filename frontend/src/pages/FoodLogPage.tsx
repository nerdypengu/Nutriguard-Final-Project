import { useState, useEffect } from 'react';
import { PlusCircle, UtensilsCrossed, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { api } from '../utils/api';

export default function FoodLogPage() {
  const { user } = useAuth();
  
  const [foodName, setFoodName] = useState('');
  const [calories, setCalories] = useState('');
  const [protein, setProtein] = useState('');
  const [carbs, setCarbs] = useState('');
  const [fat, setFat] = useState('');
  
  const [isSuccess, setIsSuccess] = useState(false);
  const [loading, setLoading] = useState(false);
  const [recentLogs, setRecentLogs] = useState<any[]>([]);

  const fetchRecentLogs = () => {
    if (!user) return;
    api.get(`/logs/user/${user.id}?limit=5`)
      .then(res => {
        if (res.success && res.data) {
          setRecentLogs(res.data);
        }
      })
      .catch(console.error);
  };

  useEffect(() => {
    fetchRecentLogs();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;
    setLoading(true);

    const logData = {
      user_id: user.id,
      food_name: foodName,
      total_calories: Number(calories),
      total_protein: Number(protein) || 0,
      total_carbs: Number(carbs) || 0,
      total_fat: Number(fat) || 0,
      logged_at: new Date().toISOString()
    };

    try {
      const res = await api.post('/logs/', logData);
      if (res.success) {
        setIsSuccess(true);
        // Reset form
        setFoodName(''); setCalories(''); setProtein(''); setCarbs(''); setFat('');
        // Refresh logs
        fetchRecentLogs();
        setTimeout(() => setIsSuccess(false), 3000);
      }
    } catch (e: any) {
      console.error(e);
      alert(e.message || "Gagal mencatat makanan.");
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (isoString: string) => {
    if (!isoString) return '';
    const date = new Date(isoString);
    return date.toLocaleDateString('id-ID', { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in duration-500">
      <div>
        <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Catat Makanan Manual</h1>
        <p className="text-slate-500 mt-1">Tambahkan detail asupan nutrisi Anda jika tidak menggunakan Discord bot.</p>
      </div>

      <div className="grid md:grid-cols-2 gap-8">
        
        {/* Form Container */}
        <div className="bg-white rounded-3xl p-6 sm:p-8 shadow-sm border border-slate-100 h-fit">
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">Nama Makanan</label>
              <input
                type="text"
                required
                value={foodName}
                onChange={(e) => setFoodName(e.target.value)}
                className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 transition-all font-medium text-slate-800"
                placeholder="Misal: Nasi Goreng Spesial"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">Kalori (kcal)</label>
              <input
                type="number"
                required
                min="0"
                value={calories}
                onChange={(e) => setCalories(e.target.value)}
                className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 transition-all font-medium text-slate-800"
                placeholder="0"
              />
            </div>

            <div className="pt-4 border-t border-slate-100">
              <h3 className="text-sm font-bold text-slate-800 mb-4 uppercase tracking-wider">Makronutrisi (Opsional)</h3>
              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-500 mb-1">Protein (g)</label>
                  <input
                    type="number"
                    min="0"
                    value={protein}
                    onChange={(e) => setProtein(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
                    placeholder="0"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-500 mb-1">Karbo (g)</label>
                  <input
                    type="number"
                    min="0"
                    value={carbs}
                    onChange={(e) => setCarbs(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
                    placeholder="0"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-500 mb-1">Lemak (g)</label>
                  <input
                    type="number"
                    min="0"
                    value={fat}
                    onChange={(e) => setFat(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
                    placeholder="0"
                  />
                </div>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 py-4 px-4 mt-8 border border-transparent rounded-xl shadow-sm text-base font-bold text-white bg-emerald-600 hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 disabled:opacity-70 transition-all"
            >
              {isSuccess ? <CheckCircle2 className="w-5 h-5 animate-bounce" /> : <PlusCircle className="w-5 h-5" />}
              {isSuccess ? 'Berhasil Disimpan!' : (loading ? 'Menyimpan...' : 'Simpan Makanan')}
            </button>
          </form>
        </div>

        {/* Recent Logs Preview */}
        <div>
          <h2 className="text-xl font-bold text-slate-800 mb-4 px-1">Riwayat Terakhir</h2>
          <div className="bg-white rounded-3xl p-2 shadow-sm border border-slate-100 overflow-hidden">
            <ul className="divide-y divide-slate-100">
              {recentLogs.length > 0 ? recentLogs.map((item) => (
                <li key={item.id} className="p-4 hover:bg-slate-50 rounded-2xl transition-colors flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 bg-slate-100 rounded-full flex items-center justify-center text-slate-400">
                      <UtensilsCrossed className="w-5 h-5" />
                    </div>
                    <div>
                      <p className="font-semibold text-slate-900 leading-tight">{item.food_name}</p>
                      <p className="text-xs text-slate-500 mt-0.5">{formatDate(item.logged_at)}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="text-sm font-bold text-slate-700">{Math.round(item.total_calories)} kcal</span>
                  </div>
                </li>
              )) : (
                <li className="p-6 text-center text-slate-500 text-sm">Belum ada makanan yang dicatat.</li>
              )}
            </ul>
          </div>
        </div>

      </div>
    </div>
  );
}
