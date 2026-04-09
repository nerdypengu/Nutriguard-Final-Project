import { Utensils } from 'lucide-react';
import { Link, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export function TopBarLayout() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="flex flex-col min-h-screen bg-slate-50 font-sans">
      <header className="bg-white border-b border-slate-200 sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 md:px-8 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 text-emerald-600 group">
            <div className="p-1.5 bg-emerald-100 rounded-lg group-hover:bg-emerald-200 transition-colors">
              <Utensils className="w-6 h-6" />
            </div>
            <span className="text-xl font-bold tracking-tight group-hover:text-emerald-700 transition-colors">NutriGuard</span>
          </Link>
          <nav>
            {isAuthenticated ? (
              <Link to="/dashboard" className="bg-emerald-600 text-white px-5 py-2.5 rounded-xl font-bold hover:bg-emerald-700 transition shadow-sm hover:shadow-md hover:shadow-emerald-200">
                Dashboard
              </Link>
            ) : (
              <Link to="/login" className="bg-emerald-600 text-white px-5 py-2.5 rounded-xl font-bold hover:bg-emerald-700 transition shadow-sm hover:shadow-md hover:shadow-emerald-200">
                Masuk
              </Link>
            )}
          </nav>
        </div>
      </header>
      <main className="flex-1 w-full max-w-6xl mx-auto px-4 md:px-8 py-8 md:py-12 flex flex-col">
        <Outlet />
      </main>
    </div>
  );
}
