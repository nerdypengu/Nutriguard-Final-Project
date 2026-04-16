import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../utils/api';
import { CalendarDays, PlusCircle, CheckCircle2, AlertCircle, Calendar, Pencil, Save, X, Target } from 'lucide-react';

interface MealPlan {
  id: string;
  user_id: string;
  food_name: string;
  meal_type: 'BREAKFAST' | 'LUNCH' | 'DINNER' | 'SNACK';
  plan_date: string;
  target_calories: number;
  target_protein: number;
  target_carbs: number;
  target_fat: number;
  status: 'PLANNED' | 'CONSUMED' | 'SKIPPED';
  created_at: string;
  updated_at: string;
}

const MEAL_TYPES = [
  { value: 'BREAKFAST', label: 'Sarapan', color: 'bg-yellow-100 text-yellow-800 border-yellow-200' },
  { value: 'LUNCH', label: 'Makan Siang', color: 'bg-orange-100 text-orange-800 border-orange-200' },
  { value: 'DINNER', label: 'Makan Malam', color: 'bg-indigo-100 text-indigo-800 border-indigo-200' },
  { value: 'SNACK', label: 'Cemilan', color: 'bg-emerald-100 text-emerald-800 border-emerald-200' }
];

export default function MealPlansPage() {
  const { user } = useAuth();
  
  // List State
  const [plans, setPlans] = useState<MealPlan[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Filter States
  const [filterDate, setFilterDate] = useState(() => new Date().toISOString().split('T')[0]);
  const [filterType, setFilterType] = useState<string>('ALL');

  // Form State
  const [isEditing, setIsEditing] = useState<string | null>(null);
  const [formDate, setFormDate] = useState(filterDate);
  const [formFoodName, setFormFoodName] = useState('');
  const [formMealType, setFormMealType] = useState('BREAKFAST');
  const [formCalories, setFormCalories] = useState('');
  const [formProtein, setFormProtein] = useState('');
  const [formCarbs, setFormCarbs] = useState('');
  const [formFat, setFormFat] = useState('');
  
  const [formLoading, setFormLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  const fetchPlans = async () => {
    if (!user) return;
    try {
      setLoading(true);
      const data = await api.get(`/meal-plans/user/${user.id}`);
      if (data.success && data.plans) {
        setPlans(data.plans);
      } else if (Array.isArray(data)) {
        // Fallback in case endpoint returns array directly
        setPlans(data);
      }
    } catch (err) {
      console.error('Failed to load meal plans', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPlans();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

  const resetForm = () => {
    setFormFoodName('');
    setFormCalories('');
    setFormProtein('');
    setFormCarbs('');
    setFormFat('');
    setIsEditing(null);
  };

  const handleEditClick = (plan: MealPlan) => {
    setIsEditing(plan.id);
    setFormDate(plan.plan_date);
    setFormFoodName(plan.food_name);
    setFormMealType(plan.meal_type);
    setFormCalories(plan.target_calories.toString());
    setFormProtein(plan.target_protein.toString());
    setFormCarbs(plan.target_carbs.toString());
    setFormFat(plan.target_fat.toString());
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const cancelEdit = () => {
    resetForm();
    setFormDate(filterDate); // Reset to current filter day
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;
    setFormLoading(true);
    setMessage({ type: '', text: '' });

    const payload = {
      user_id: user.id,
      food_name: formFoodName,
      meal_type: formMealType,
      plan_date: formDate,
      target_calories: Number(formCalories),
      target_protein: Number(formProtein),
      target_carbs: Number(formCarbs),
      target_fat: Number(formFat)
    };

    try {
      if (isEditing) {
        await api.put(`/meal-plans/${isEditing}`, payload);
        setMessage({ type: 'success', text: 'Rencana makan berhasil diperbarui!' });
      } else {
        await api.post('/meal-plans/', payload);
        setMessage({ type: 'success', text: 'Rencana makan berhasil ditambahkan!' });
      }
      
      resetForm();
      fetchPlans(); // Refresh the list
      setTimeout(() => setMessage({ type: '', text: '' }), 4000);
    } catch (error: any) {
      setMessage({ type: 'error', text: error.message || 'Gagal menyimpan rencana makan.' });
    } finally {
      setFormLoading(false);
    }
  };

  // Filtered Results
  const filteredPlans = plans
    .filter(plan => plan.plan_date === filterDate)
    .filter(plan => filterType === 'ALL' || plan.meal_type === filterType)
    .sort((a, b) => {
      // Sort logically by meal type progression
      const order = { 'BREAKFAST': 1, 'LUNCH': 2, 'DINNER': 3, 'SNACK': 4 };
      // @ts-ignore
      return (order[a.meal_type] || 5) - (order[b.meal_type] || 5);
    });

  const getBadgeStyles = (type: string) => {
    const found = MEAL_TYPES.find(m => m.value === type);
    return found ? found.color : 'bg-slate-100 text-slate-800 border-slate-200';
  };

  const getBadgeLabel = (type: string) => {
    const found = MEAL_TYPES.find(m => m.value === type);
    return found ? found.label : type;
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-in fade-in duration-500">
      <div>
        <h1 className="text-3xl font-bold text-slate-900 tracking-tight flex items-center gap-3">
          <CalendarDays className="w-8 h-8 text-emerald-600" />
          Rencana Makan
        </h1>
        <p className="text-slate-500 mt-1">Buat jadwal makan dan atur target makronutrisi harian Anda di sini.</p>
      </div>

      {message.text && (
        <div className={`p-4 rounded-xl flex items-center gap-3 animate-in fade-in ${message.type === 'success' ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-rose-50 text-rose-800 border border-rose-200'}`}>
          {message.type === 'success' ? <CheckCircle2 className="w-5 h-5 text-emerald-500" /> : <AlertCircle className="w-5 h-5 text-rose-500" />}
          <p className="font-medium">{message.text}</p>
        </div>
      )}

      {/* Form Section */}
      <div className={`bg-white rounded-3xl p-6 sm:p-8 shadow-sm border ${isEditing ? 'border-amber-300 ring-4 ring-amber-50' : 'border-slate-100'}`}>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2">
            {isEditing ? <Pencil className="w-5 h-5 text-amber-500" /> : <PlusCircle className="w-5 h-5 text-emerald-500" />}
            {isEditing ? 'Edit Rencana Makan' : 'Buat Rencana Baru'}
          </h2>
          {isEditing && (
            <button onClick={cancelEdit} className="text-sm font-semibold text-slate-500 hover:text-rose-500 transition-colors flex items-center gap-1">
              <X className="w-4 h-4" /> Batal Edit
            </button>
          )}
        </div>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid md:grid-cols-3 gap-6">
            <div className="col-span-1 md:col-span-1">
              <label className="block text-sm font-semibold text-slate-700 mb-2">Tanggal</label>
              <input
                type="date"
                required
                value={formDate}
                onChange={(e) => setFormDate(e.target.value)}
                className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 transition-all font-medium text-slate-800"
              />
            </div>
            
            <div className="col-span-1 md:col-span-1">
              <label className="block text-sm font-semibold text-slate-700 mb-2">Tipe Makan</label>
              <select
                required
                value={formMealType}
                onChange={(e) => setFormMealType(e.target.value)}
                className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 font-medium text-slate-800"
              >
                {MEAL_TYPES.map(type => (
                  <option key={`form-${type.value}`} value={type.value}>{type.label}</option>
                ))}
              </select>
            </div>

            <div className="col-span-1 md:col-span-1">
              <label className="block text-sm font-semibold text-slate-700 mb-2">Nama Menu</label>
              <input
                type="text"
                required
                value={formFoodName}
                onChange={(e) => setFormFoodName(e.target.value)}
                className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 transition-all font-medium text-slate-800"
                placeholder="Misal: Oatmeal Pisang"
              />
            </div>
          </div>

          <div className="pt-4 border-t border-slate-100">
            <h3 className="text-sm font-bold text-slate-800 mb-4 flex items-center gap-2">
              <Target className="w-4 h-4 text-emerald-600" />
              Target Nutrisi (Wajib)
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-500 mb-1">Kalori (kcal)</label>
                <input
                  type="number" required min="1"
                  value={formCalories} onChange={(e) => setFormCalories(e.target.value)}
                  className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  placeholder="0"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-500 mb-1">Protein (g)</label>
                <input
                  type="number" required min="0" step="0.1"
                  value={formProtein} onChange={(e) => setFormProtein(e.target.value)}
                  className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  placeholder="0"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-500 mb-1">Karbo (g)</label>
                <input
                  type="number" required min="0" step="0.1"
                  value={formCarbs} onChange={(e) => setFormCarbs(e.target.value)}
                  className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  placeholder="0"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-500 mb-1">Lemak (g)</label>
                <input
                  type="number" required min="0" step="0.1"
                  value={formFat} onChange={(e) => setFormFat(e.target.value)}
                  className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  placeholder="0"
                />
              </div>
            </div>
          </div>

          <button
            type="submit"
            disabled={formLoading}
            className={`w-full flex items-center justify-center gap-2 py-4 px-4 border border-transparent rounded-xl shadow-sm text-base font-bold text-white focus:outline-none focus:ring-2 focus:ring-offset-2 transition-all ${isEditing ? 'bg-amber-500 hover:bg-amber-600 focus:ring-amber-500' : 'bg-emerald-600 hover:bg-emerald-700 focus:ring-emerald-500'} disabled:opacity-70`}
          >
            {isEditing ? <Save className="w-5 h-5" /> : <PlusCircle className="w-5 h-5" />}
            {formLoading ? 'Menyimpan...' : (isEditing ? 'Simpan Perubahan' : 'Tambahkan ke Jadwal')}
          </button>
        </form>
      </div>

      {/* List & Filter Section */}
      <div className="bg-white rounded-3xl p-6 sm:p-8 shadow-sm border border-slate-100">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
          <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2">
            <Calendar className="w-5 h-5 text-slate-500" />
            Daftar Jadwal
          </h2>
          
          <div className="flex flex-col sm:flex-row gap-3">
            <input
              type="date"
              value={filterDate}
              onChange={(e) => setFilterDate(e.target.value)}
              className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm font-medium text-slate-700 focus:ring-2 focus:ring-emerald-500"
            />
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm font-medium text-slate-700 focus:ring-2 focus:ring-emerald-500"
            >
              <option value="ALL">Semua Tipe</option>
              {MEAL_TYPES.map(type => (
                <option key={`filter-${type.value}`} value={type.value}>{type.label}</option>
              ))}
            </select>
          </div>
        </div>

        {loading ? (
          <div className="py-12 text-center text-slate-400">Memuat data kalender...</div>
        ) : filteredPlans.length === 0 ? (
          <div className="py-12 text-center flex flex-col items-center">
            <div className="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mb-3">
              <CalendarDays className="w-8 h-8 text-slate-300" />
            </div>
            <p className="text-slate-500 font-medium">Tidak ada rencana makan untuk filter ini.</p>
            <p className="text-sm text-slate-400 mt-1">Gunakan form di atas untuk menambah menu.</p>
          </div>
        ) : (
          <div className="grid gap-4">
            {filteredPlans.map(plan => (
              <div key={plan.id} className="border border-slate-100 rounded-2xl p-5 hover:border-emerald-200 hover:shadow-md transition-all bg-white group">
                <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-3 mb-2">
                      <span className={`px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider rounded-md border ${getBadgeStyles(plan.meal_type)}`}>
                        {getBadgeLabel(plan.meal_type)}
                      </span>
                      <span className="text-xs font-semibold text-slate-400">
                        {new Date(plan.plan_date).toLocaleDateString('id-ID', { year: 'numeric', month: 'long', day: 'numeric' })}
                      </span>
                    </div>
                    <h3 className="text-lg font-bold text-slate-900 leading-tight">{plan.food_name}</h3>
                  </div>

                  <div className="flex items-center gap-6">
                    <div className="grid grid-cols-4 gap-4 text-center md:text-left text-sm">
                      <div>
                         <p className="text-slate-400 text-[10px] uppercase font-bold tracking-wider mb-0.5">Kcal</p>
                         <p className="font-bold text-emerald-600">{Math.round(plan.target_calories)}</p>
                      </div>
                      <div>
                         <p className="text-slate-400 text-[10px] uppercase font-bold tracking-wider mb-0.5">Pro</p>
                         <p className="font-semibold text-slate-700">{Math.round(plan.target_protein)}g</p>
                      </div>
                      <div>
                         <p className="text-slate-400 text-[10px] uppercase font-bold tracking-wider mb-0.5">Carb</p>
                         <p className="font-semibold text-slate-700">{Math.round(plan.target_carbs)}g</p>
                      </div>
                      <div>
                         <p className="text-slate-400 text-[10px] uppercase font-bold tracking-wider mb-0.5">Fat</p>
                         <p className="font-semibold text-slate-700">{Math.round(plan.target_fat)}g</p>
                      </div>
                    </div>
                    
                    <div className="pl-4 border-l border-slate-100">
                      <button
                        onClick={() => handleEditClick(plan)}
                        className="p-2 text-slate-400 hover:text-amber-500 hover:bg-amber-50 rounded-lg transition-colors"
                        title="Edit Rencana"
                      >
                        <Pencil className="w-5 h-5" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
