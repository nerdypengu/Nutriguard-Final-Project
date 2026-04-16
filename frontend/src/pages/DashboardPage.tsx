import { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { Flame, Droplets, Dumbbell, Cookie, UtensilsCrossed, CalendarDays, Target } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { api } from '../utils/api';
import { realtimeSupabase, setupRealtimeAuth } from '../utils/supabase';

export default function DashboardPage() {
  const { user } = useAuth();
  
  // States
  const [loading, setLoading] = useState(true);
  const [totals, setTotals] = useState({ calories: 0, protein: 0, carbs: 0, fat: 0 });
  const [targets, setTargets] = useState({ calories: 2000, protein: 120, carbs: 250, fat: 65 });
  const [meals, setMeals] = useState<Array<{ id: string; food_name: string; logged_at: string; total_protein: number; total_carbs: number; total_fat: number; total_calories: number }>>([]);
  const [mealPlans, setMealPlans] = useState<Array<{ id: string; meal_type: string; meal_name: string; total_protein: number; total_carbs: number; total_fat: number; total_calories: number }>>([]);

  useEffect(() => {
    if (!user) return;

    const today = new Date().toISOString().split('T')[0];

    const fetchDashboardData = async () => {
      try {
        // Fetch Preferences for Targets
        const prefRes = await api.get(`/users/${user.id}/preferences`).catch(() => ({}));
        if (prefRes.success && prefRes.data) {
          setTargets({
            calories: prefRes.data.target_calories || 2000,
            protein: prefRes.data.target_protein_g || 120,
            carbs: prefRes.data.target_carbs_g || 250,
            fat: prefRes.data.target_fat_g || 65,
          });
        }

        // Fetch Today's Totals
        const totalsRes = await api.get(`/logs/user/${user.id}/totals/${today}`);
        if (totalsRes.success && totalsRes.data) {
          setTotals({
            calories: totalsRes.data.total_calories || 0,
            protein: totalsRes.data.total_protein || 0,
            carbs: totalsRes.data.total_carbs || 0,
            fat: totalsRes.data.total_fat || 0,
          });
        }

        // Fetch Today's Meals
        const mealsRes = await api.get(`/logs/user/${user.id}/date/${today}`);
        if (mealsRes.success && mealsRes.data) {
          setMeals(mealsRes.data);
        }

        // Fetch Today's Meal Plans
        const plansRes = await api.get(`/meal-plans/user/${user.id}/current`).catch(() => ({}));
        // Robust handling of both 'data' and 'plans' property names
        const fetchedPlans = plansRes.data || plansRes.plans || (Array.isArray(plansRes) ? plansRes : []);
        setMealPlans(fetchedPlans);

      } catch (error) {
        console.error("Failed to load dashboard data", error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    let realtimeChannel: any = null;

    const setupRealtime = async () => {
      if (!realtimeSupabase) return;
      
      try {
        const tokenRes = await api.get('/auth/realtime-token').catch(() => ({}));
        if (tokenRes.success && tokenRes.access_token) {
          setupRealtimeAuth(tokenRes.access_token);
        }

        realtimeChannel = realtimeSupabase.channel('dashboard-channel-logs')
          .on(
            'postgres_changes',
            { event: '*', schema: 'nutriguard', table: 'consumption_logs', filter: `user_id=eq.${user.id}` },
            () => {
              // Whenever a log changes, refresh the dash
              fetchDashboardData();
            }
          )
          .subscribe();
      } catch (err) {
        console.error('Failed to setup realtime listening', err);
      }
    };

    setupRealtime();

    return () => {
      if (realtimeChannel && realtimeSupabase) {
        realtimeSupabase.removeChannel(realtimeChannel);
      }
    };
  }, [user]);

  if (loading) {
     return <div className="p-10 text-center text-slate-500">Memuat dashboard...</div>;
  }

  const REMAINING = targets.calories - totals.calories;
  const chartData = [
    { name: 'Consumed', value: totals.calories, color: '#10b981' },
    { name: 'Remaining', value: REMAINING > 0 ? REMAINING : 0, color: '#f1f5f9' },
  ];

  const getPercentage = (consumed: number, target: number) => {
    if (!target) return 0;
    return Math.min(100, Math.round((consumed / target) * 100));
  };

  const formatDate = (isoString: string) => {
    if (!isoString) return '';
    const date = new Date(isoString);
    return date.toLocaleDateString('id-ID', { hour: '2-digit', minute: '2-digit' });
  };

  const MEAL_TYPES_LABELS: Record<string, string> = {
    'BREAKFAST': 'Sarapan',
    'LUNCH': 'Makan Siang',
    'DINNER': 'Makan Malam',
    'ADDITIONAL': 'Cemilan'
  };

  const getBadgeStyles = (type: string) => {
    switch (type) {
      case 'BREAKFAST': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'LUNCH': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'DINNER': return 'bg-indigo-100 text-indigo-800 border-indigo-200';
      case 'ADDITIONAL': return 'bg-emerald-100 text-emerald-800 border-emerald-200';
      default: return 'bg-slate-100 text-slate-800 border-slate-200';
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div>
        <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Halo, {user?.discord_username || user?.email.split('@')[0]}!</h1>
        <p className="text-slate-500 mt-1">Berikut adalah ringkasan asupan nutrisi Anda hari ini.</p>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Chart Section */}
        <div className="lg:col-span-2 bg-white rounded-3xl p-8 shadow-sm border border-slate-100 relative">
          <h2 className="text-xl font-bold text-slate-800 mb-6">Kalori Harian</h2>
          
          <div className="h-72 relative flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={chartData}
                  cx="50%"
                  cy="50%"
                  innerRadius={80}
                  outerRadius={120}
                  startAngle={90}
                  endAngle={-270}
                  paddingAngle={2}
                  dataKey="value"
                  stroke="none"
                  animationDuration={1500}
                >
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ borderRadius: '12px', border: '1px solid #e2e8f0', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                  itemStyle={{ color: '#0f172a', fontWeight: 600 }}
                />
              </PieChart>
            </ResponsiveContainer>
            
            <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
              <span className="text-5xl font-extrabold text-slate-900 tracking-tighter">
                {Math.round(totals.calories)}
              </span>
              <span className="text-sm font-medium text-slate-500 mt-1">/ {targets.calories} kcal</span>
            </div>
          </div>

          <div className="mt-6 grid grid-cols-2 gap-4">
            <div className="bg-emerald-50 rounded-2xl p-4 flex flex-col items-center justify-center">
              <span className="text-emerald-600 font-semibold mb-1">Terisi</span>
              <span className="text-2xl font-bold text-slate-900">{Math.round(totals.calories)}</span>
            </div>
            <div className="bg-slate-50 rounded-2xl p-4 flex flex-col items-center justify-center">
              <span className="text-slate-500 font-semibold mb-1">Sisa</span>
              <span className="text-2xl font-bold text-slate-900">{Math.round(REMAINING > 0 ? REMAINING : 0)}</span>
            </div>
          </div>
        </div>

        {/* Macros Summary */}
        <div className="space-y-4">
          <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100 flex items-center gap-5">
            <div className="w-14 h-14 rounded-2xl bg-orange-100 text-orange-500 flex items-center justify-center shrink-0">
              <Dumbbell className="w-7 h-7" />
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-slate-500 mb-1">Protein</p>
              <div className="flex justify-between items-end">
                <p className="text-2xl font-bold text-slate-900">{Math.round(totals.protein)}<span className="text-base font-medium text-slate-500 ml-1">g</span></p>
                <p className="text-sm text-slate-400">/ {targets.protein}g</p>
              </div>
              <div className="w-full bg-slate-100 h-2 rounded-full mt-2">
                <div className="bg-orange-500 h-full rounded-full" style={{ width: `${getPercentage(totals.protein, targets.protein)}%` }}></div>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100 flex items-center gap-5">
            <div className="w-14 h-14 rounded-2xl bg-amber-100 text-amber-500 flex items-center justify-center shrink-0">
              <Cookie className="w-7 h-7" />
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-slate-500 mb-1">Karbohidrat</p>
              <div className="flex justify-between items-end">
                <p className="text-2xl font-bold text-slate-900">{Math.round(totals.carbs)}<span className="text-base font-medium text-slate-500 ml-1">g</span></p>
                <p className="text-sm text-slate-400">/ {targets.carbs}g</p>
              </div>
              <div className="w-full bg-slate-100 h-2 rounded-full mt-2">
                <div className="bg-amber-500 h-full rounded-full" style={{ width: `${getPercentage(totals.carbs, targets.carbs)}%` }}></div>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100 flex items-center gap-5">
            <div className="w-14 h-14 rounded-2xl bg-red-100 text-red-500 flex items-center justify-center shrink-0">
              <Droplets className="w-7 h-7" />
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-slate-500 mb-1">Lemak</p>
              <div className="flex justify-between items-end">
                <p className="text-2xl font-bold text-slate-900">{Math.round(totals.fat)}<span className="text-base font-medium text-slate-500 ml-1">g</span></p>
                <p className="text-sm text-slate-400">/ {targets.fat}g</p>
              </div>
              <div className="w-full bg-slate-100 h-2 rounded-full mt-2">
                <div className="bg-red-500 h-full rounded-full" style={{ width: `${getPercentage(totals.fat, targets.fat)}%` }}></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Today's Meals */}
      <div>
        <h2 className="text-xl font-bold text-slate-800 mb-4 px-1">Makanan Hari Ini</h2>
        <div className="bg-white rounded-3xl shadow-sm border border-slate-100 overflow-hidden">
          <ul className="divide-y divide-slate-100">
            {meals.length > 0 ? meals.map((meal) => {
              return (
                <li key={meal.id} className="p-4 sm:px-6 hover:bg-slate-50 transition-colors flex flex-col sm:flex-row sm:items-center justify-between group gap-4">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-slate-100 rounded-xl flex items-center justify-center text-slate-500 group-hover:bg-emerald-100 group-hover:text-emerald-600 transition-colors shrink-0">
                       <UtensilsCrossed className="w-6 h-6" />
                    </div>
                    <div>
                      <p className="font-semibold text-slate-900">{meal.food_name}</p>
                      <p className="text-sm text-slate-500 flex items-center gap-2">
                        <span>Pukul {formatDate(meal.logged_at)}</span>
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4 text-sm sm:text-base ml-16 sm:ml-0">
                    <div className="hidden md:flex items-center gap-3 text-slate-500 font-medium">
                       <span>P: {Math.round(meal.total_protein)}g</span>
                       <span>C: {Math.round(meal.total_carbs)}g</span>
                       <span>F: {Math.round(meal.total_fat)}g</span>
                    </div>
                    <span className="inline-flex items-center gap-1.5 bg-emerald-50 text-emerald-700 font-bold px-3 py-1.5 rounded-lg shrink-0">
                      <Flame className="w-4 h-4 text-emerald-500" />
                      {Math.round(meal.total_calories)} kcal
                    </span>
                  </div>
                </li>
              );
            }) : (
               <li className="p-8 text-center text-slate-500">Anda belum mencatat makanan hari ini.</li>
            )}
          </ul>
        </div>
      </div>
      {/* Today's Meal Plans */}
      <div className="mt-8">
        <h2 className="text-xl font-bold text-slate-800 mb-4 px-1">Rencana Makan Hari Ini</h2>
        <div className="bg-white rounded-3xl shadow-sm border border-slate-100 overflow-hidden">
          <ul className="divide-y divide-slate-100">
            {mealPlans.length > 0 ? mealPlans.map((plan) => {
              return (
                <li key={`plan-${plan.id}`} className="p-4 sm:px-6 hover:bg-slate-50 transition-colors flex flex-col md:flex-row md:items-center justify-between group gap-4">
                  <div className="flex items-start md:items-center gap-4">
                    <div className="w-12 h-12 bg-slate-100 rounded-xl flex items-center justify-center text-slate-400 group-hover:bg-indigo-100 group-hover:text-indigo-600 transition-colors shrink-0">
                       <CalendarDays className="w-6 h-6" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                         <span className={`px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider rounded border ${getBadgeStyles(plan.meal_type)}`}>
                            {MEAL_TYPES_LABELS[plan.meal_type] || plan.meal_type}
                         </span>
                      </div>
                      <p className="font-semibold text-slate-900 leading-tight">{plan.meal_name}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4 text-sm sm:text-base ml-16 md:ml-0">
                    <div className="hidden lg:flex items-center gap-3 text-slate-500 font-medium">
                       <span>P: {Math.round(plan.total_protein)}g</span>
                       <span>C: {Math.round(plan.total_carbs)}g</span>
                       <span>F: {Math.round(plan.total_fat)}g</span>
                    </div>
                    <span className="inline-flex items-center gap-1.5 bg-slate-100 text-slate-700 font-bold px-3 py-1.5 rounded-lg shrink-0">
                      <Target className="w-4 h-4 text-slate-400" />
                      {Math.round(plan.total_calories)} kcal target
                    </span>
                  </div>
                </li>
              );
            }) : (
               <li className="p-8 text-center text-slate-500">Anda belum membuat rencana makan untuk hari ini.</li>
            )}
          </ul>
        </div>
      </div>
    </div>
  );
}
