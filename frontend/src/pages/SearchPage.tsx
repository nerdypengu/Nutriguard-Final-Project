import { useState } from 'react';
import { Search, Plus, Info, Loader2 } from 'lucide-react';
import { api } from '../utils/api';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

export default function SearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [searchedPhrase, setSearchedPhrase] = useState('');
  
  const { user } = useAuth();
  const navigate = useNavigate();

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsSearching(true);
    setSearchedPhrase(query);

    try {
      const res = await api.get(`/food/search/by-name?name=${encodeURIComponent(query)}`);
      if (res.success) {
        setResults(res.data || []);
      }
    } catch (e) {
      console.error("Search failed", e);
    } finally {
      setIsSearching(false);
    }
  };

  const handleLogFood = async (food: any) => {
    if (!user) return;
    try {
      const logData = {
        user_id: user.id,
        food_name: food.name,
        total_calories: food.calories,
        total_protein: food.protein_g,
        total_carbs: food.carbs_g,
        total_fat: food.fat_g,
        logged_at: new Date().toISOString()
      };
      
      const res = await api.post('/logs/', logData);
      if (res.success) {
         alert(`${food.name} berhasil dicatat!`);
         navigate('/dashboard');
      }
    } catch (e) {
       console.error(e);
       alert("Gagal mencatat makanan");
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-in fade-in duration-500">
      <div className="text-center max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold text-slate-900 tracking-tight mb-6">Database Makronutrisi</h1>
        <form onSubmit={handleSearch} className="relative group">
          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
            <Search className="h-6 w-6 text-slate-400 group-focus-within:text-emerald-500 transition-colors" />
          </div>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="block w-full pl-14 pr-24 py-4 bg-white border-2 border-slate-100 rounded-2xl text-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:border-emerald-500 focus:ring-4 focus:ring-emerald-500/10 transition-all shadow-sm group-hover:shadow-md"
            placeholder="Cari kandungan gizi makanan..."
          />
          <button 
            type="submit"
            disabled={isSearching}
            className="absolute inset-y-2 right-2 bg-slate-900 text-white px-6 rounded-xl font-medium hover:bg-slate-800 transition-colors disabled:opacity-70 flex items-center gap-2"
          >
            {isSearching ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Cari'}
          </button>
        </form>
      </div>

      {(searchedPhrase || results.length > 0) && (
        <div className="mt-8 space-y-4">
          <div className="flex items-center justify-between px-1">
            <p className="text-slate-500 font-medium">Menampilkan hasil untuk: <span className="text-slate-900 font-bold">{searchedPhrase}</span></p>
            <div className="text-sm text-slate-400 flex items-center gap-1">
              <Info className="w-4 h-4"/> Data estimasi per 1 porsi (berdasarkan db)
            </div>
          </div>

          {results.length === 0 && !isSearching ? (
             <div className="bg-white p-10 rounded-3xl text-center border border-slate-100 shadow-sm">
                <p className="text-slate-500">Makanan tidak ditemukan di database. Cobalah mencari dengan kata kunci lain atau catat secara manual.</p>
             </div>
          ) : (
            <div className="grid gap-4">
              {results.map((food: any) => (
                <div key={food.id} className="bg-white p-5 rounded-3xl shadow-sm border border-slate-100 hover:border-emerald-200 transition-all hover:shadow-md flex flex-col md:flex-row md:items-center justify-between gap-6 group">
                  
                  <div className="flex-1">
                    <h3 className="text-xl font-bold text-slate-900 mb-1">{food.name}</h3>
                    <p className="text-emerald-600 font-bold mb-4">{food.calories} kcal</p>
                    
                    <div className="flex flex-wrap gap-4">
                      <div className="flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-orange-500"></span>
                        <span className="text-sm font-medium text-slate-600">Protein:</span>
                        <span className="text-sm font-bold text-slate-900">{food.protein_g}g</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-amber-500"></span>
                        <span className="text-sm font-medium text-slate-600">Karbo:</span>
                        <span className="text-sm font-bold text-slate-900">{food.carbs_g}g</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-red-500"></span>
                        <span className="text-sm font-medium text-slate-600">Lemak:</span>
                        <span className="text-sm font-bold text-slate-900">{food.fat_g}g</span>
                      </div>
                    </div>
                  </div>

                  <button 
                     onClick={() => handleLogFood(food)}
                     className="flex items-center justify-center gap-2 bg-emerald-50 text-emerald-700 md:w-auto w-full py-3 px-6 rounded-xl font-bold border border-emerald-100 hover:bg-emerald-600 hover:text-white transition-all duration-300 transform group-hover:scale-105"
                  >
                    <Plus className="w-5 h-5" />
                    Catat Makanan
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
