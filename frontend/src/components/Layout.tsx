import { useState, useEffect } from 'react';
import { NavLink, useLocation, Outlet, useNavigate } from 'react-router-dom';
import { Home, LayoutDashboard, Utensils, Search, Settings, Menu, X, LogOut, MessageSquare, FileText } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { api } from '../utils/api';

const navItems = [
  { path: '/', name: 'Home', icon: Home },
  { path: '/dashboard', name: 'Dashboard', icon: LayoutDashboard },
  { path: '/meal-plans', name: 'Rencana Makan', icon: FileText },
  { path: '/log', name: 'Catat Makanan', icon: Utensils },
  { path: '/search', name: 'Database Gizi', icon: Search },
  { path: '/profile', name: 'Profil', icon: Settings },
  { path: '/integrations', name: 'Discord Bot', icon: MessageSquare },
  { path: '/meal-chat', name: 'Tanya AI Kami', icon: MessageSquare },
];

export function Layout() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [hasFailedJob, setHasFailedJob] = useState(false);

  useEffect(() => {
    if (!user) return;
    
    const checkJobs = async () => {
      try {
        const response = await api.get('/meal-processing/jobs?limit=5');
        if (response && response.jobs) {
          const failed = response.jobs.some((job: any) => job.status === 'FAILED');
          setHasFailedJob(failed);
        }
      } catch (e) {
        // Silently omit error
      }
    };

    checkJobs();
    const interval = setInterval(checkJobs, 15000); // Check every 15s
    return () => clearInterval(interval);
  }, [user, location.pathname]); // re-check when path changes so we can see updates

  const closeSidebar = () => setIsSidebarOpen(false);

  return (
    <div className="flex h-screen bg-slate-50 text-slate-900 font-sans">
      {/* Mobile Sidebar Overlay */}
      {isSidebarOpen && (
        <div 
          className="fixed inset-0 z-20 bg-slate-900/50 backdrop-blur-sm lg:hidden transition-opacity"
          onClick={closeSidebar}
        />
      )}

      {/* Sidebar */}
      <aside className={`
        fixed inset-y-0 left-0 z-30 w-72 bg-white border-r border-slate-200 transform transition-transform duration-300 ease-in-out flex flex-col
        ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        lg:translate-x-0 lg:static lg:inset-auto
      `}>
        <div className="flex items-center justify-between h-16 px-6 border-b border-slate-200">
          <div className="flex items-center gap-2 text-emerald-600">
            <div className="p-1.5 bg-emerald-100 rounded-lg">
              <Utensils className="w-6 h-6" />
            </div>
            <span className="text-xl font-bold tracking-tight">NutriGuard</span>
          </div>
          <button onClick={closeSidebar} className="lg:hidden text-slate-500 hover:text-slate-700">
            <X className="w-6 h-6" />
          </button>
        </div>

        <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={closeSidebar}
                className={`
                  flex items-center gap-3 px-3 py-3 rounded-xl transition-all duration-200 group relative
                  ${isActive 
                    ? 'bg-emerald-500 text-white shadow-md shadow-emerald-200 font-medium' 
                    : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'}
                `}
              >
                <Icon className={`w-5 h-5 ${isActive ? 'text-white' : 'text-slate-400 group-hover:text-emerald-500'}`} />
                {item.name}
                {item.path === '/meal-chat' && hasFailedJob && (
                  <span className="absolute right-3 w-2.5 h-2.5 bg-rose-500 rounded-full animate-pulse shadow-sm shadow-rose-200"></span>
                )}
              </NavLink>
            );
          })}
        </nav>

        <div className="p-4 border-t border-slate-200">
          <button
            onClick={() => {
              closeSidebar();
              logout();
              navigate('/');
            }}
            className="w-full flex items-center gap-3 px-3 py-3 rounded-xl text-slate-600 hover:bg-rose-50 hover:text-rose-600 transition-all group"
          >
            <LogOut className="w-5 h-5 text-slate-400 group-hover:text-rose-500" />
            <span className="font-medium">Logout</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Mobile Header */}
        <header className="lg:hidden bg-white border-b border-slate-200 h-16 flex items-center justify-between px-4 z-10 shrink-0">
          <div className="flex items-center gap-2 text-emerald-600">
             <Utensils className="w-5 h-5" />
             <span className="text-lg font-bold">NutriGuard</span>
          </div>
          <button 
            onClick={() => setIsSidebarOpen(true)}
            className="p-2 mr-[-8px] text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
          >
            <Menu className="w-6 h-6" />
          </button>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto p-4 md:p-8 lg:p-10">
          <div className="mx-auto max-w-6xl w-full h-full">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
