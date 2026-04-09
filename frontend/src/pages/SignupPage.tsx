import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Mail, Lock, ArrowRight, AlertCircle, UserPlus } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { api } from '../utils/api';

export default function SignupPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleKeycloakSignup = () => {
    const keycloakUrl = import.meta.env.VITE_KEYCLOAK_URL || 'http://localhost:8080';
    const realm = import.meta.env.VITE_KEYCLOAK_REALM || 'nutriguard';
    const clientId = import.meta.env.VITE_KEYCLOAK_CLIENT_ID || 'nutriguard-backend';
    const redirectUri = encodeURIComponent(`${window.location.origin}/auth/callback`);
    
    // We can usually append kc_action=register if we strictly want keycloak to show register page first
    // For universal login, standard auth URL is fine, but kc_action helps
    const authUrl = `${keycloakUrl}/realms/${realm}/protocol/openid-connect/auth?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=code&scope=openid email profile&kc_action=register`;
    
    window.location.href = authUrl;
  };

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      setErrorMsg("Password tidak sama.");
      return;
    }

    setLoading(true);
    setErrorMsg('');
    
    try {
      const response = await api.post('/auth/signup', { email, password });
      if (response.success && response.user) {
         // Auto sign-in after sign up usually requires hitting signin or we can just redirect to login
         // But the backend auth implementation returns an access_token on signup or signin?
         // Let's assume we need to sign in to get the token, or if signup returns it we use it.
         // Looking at backend code from earlier: signup doesn't return access_token natively unless modified
         // Actually we can just log them in using the signin endpoint automatically
         const loginRes = await api.post('/auth/signin', { email, password });
         if (loginRes.success && loginRes.access_token) {
            login(loginRes.user, loginRes.access_token);
            // Since this is a new signup via email, we know they are new. Redirect to onboarding!
            navigate('/onboarding');
         } else {
             setErrorMsg('Pendaftaran berhasil, tetapi gagal masuk otomatis. Silakan login manual.');
         }
      } else {
        setErrorMsg(response.message || 'Pendaftaran gagal, periksa data Anda.');
      }
    } catch (error: any) {
      setErrorMsg(error.message || 'Terjadi kesalahan saat pendaftaran.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-[80vh] animate-in fade-in duration-500">
      <div className="w-full max-w-md bg-white p-10 rounded-3xl shadow-xl shadow-slate-200/50 border border-slate-100">
        <div className="flex flex-col items-center mb-6">
          <div className="w-16 h-16 bg-emerald-100 text-emerald-600 rounded-2xl flex items-center justify-center mb-4">
            <UserPlus className="w-8 h-8" />
          </div>
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Daftar Akun</h1>
          <p className="text-slate-500 mt-2">Mulai perjalanan sehat Anda</p>
        </div>

        {errorMsg && (
          <div className="mb-6 p-4 bg-rose-50 rounded-xl flex items-start gap-3 border border-rose-100 animate-in slide-in-from-top-2">
            <AlertCircle className="w-5 h-5 text-rose-500 shrink-0 mt-0.5" />
            <p className="text-sm font-medium text-rose-700">{errorMsg}</p>
          </div>
        )}

        <div className="space-y-4 mb-6">
           <button
             type="button"
             onClick={handleKeycloakSignup}
             className="w-full flex items-center justify-center gap-3 py-3.5 px-4 border-2 border-slate-200 rounded-xl shadow-sm text-sm font-bold text-slate-700 bg-white hover:bg-slate-50 focus:outline-none transition-all"
           >
             <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="text-indigo-600"><path d="M2 18v3c0 .6.4 1 1 1h4v-3h3v-3h2l1.4-1.4a6.5 6.5 0 1 0-4-4Z"/><circle cx="16.5" cy="7.5" r=".5" fill="currentColor"/></svg>
             Sign Up with Keycloak
           </button>
        </div>

        <div className="relative mb-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-slate-200" />
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-3 bg-white text-slate-500 font-medium">Atau Daftar dengan email</span>
          </div>
        </div>

        <form onSubmit={handleSignup} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5 ml-1">Email</label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <Mail className="h-5 w-5 text-slate-400" />
              </div>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="block w-full pl-11 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                placeholder="anda@email.com"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5 ml-1">Password</label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <Lock className="h-5 w-5 text-slate-400" />
              </div>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="block w-full pl-11 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                placeholder="••••••••"
              />
            </div>
          </div>
          
           <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5 ml-1">Konfirmasi Password</label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <Lock className="h-5 w-5 text-slate-400" />
              </div>
              <input
                type="password"
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="block w-full pl-11 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                placeholder="••••••••"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 py-3.5 px-4 mt-6 border border-transparent rounded-xl shadow-sm text-sm font-bold text-white bg-emerald-600 hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 disabled:opacity-70 disabled:cursor-not-allowed transition-all"
          >
            {loading ? 'Memproses...' : 'Sign Up'}
            {!loading && <ArrowRight className="w-4 h-4" />}
          </button>
        </form>

        <div className="mt-8 text-center border-t border-slate-100 pt-6">
          <p className="text-sm text-slate-600">
            Sudah punya akun?{' '}
            <button onClick={() => navigate('/login')} className="font-bold text-emerald-600 hover:text-emerald-700 transition-colors">
              Sign In
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}
