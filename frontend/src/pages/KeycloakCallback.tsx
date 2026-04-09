import { useEffect, useState, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { api } from '../utils/api';
import { Loader2 } from 'lucide-react';

export default function KeycloakCallback() {
  const [errorMsg, setErrorMsg] = useState('');
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();
  
  // Prevent double calling in React Strict Mode
  const processedRef = useRef(false);

  useEffect(() => {
    if (processedRef.current) return;
    
    // We get the ?code= query param returned by Keycloak
    const params = new URLSearchParams(location.search);
    const code = params.get('code');
    const redirectUri = `${window.location.origin}/auth/callback`;

    if (!code) {
      setErrorMsg('No authorization code found from Keycloak. Make sure you logged in correctly.');
      processedRef.current = true;
      return;
    }

    processedRef.current = true;

    const authenticateWithKeycloak = async () => {
      try {
        const response = await api.post('/auth/keycloak', { code, redirect_uri: redirectUri });
        
        if (response.success && response.access_token) {
          // Log user into context securely
          login(response.user, response.access_token);
          
          // Check if user is "new" by verifying if preferences exist
          try {
            const prefs = await api.get(`/users/${response.user.id}/preferences`);
            if (prefs.success && prefs.data && prefs.data.target_calories) {
              // Existing user with preferences, go to dashboard
              navigate('/dashboard');
            } else {
              // Preferences exist but empty or weird shape, just go to onboarding
              navigate('/onboarding');
            }
          } catch (e: any) {
            console.log('Preferences check failed, likely a new user', e);
            // 404 means no preferences -> new user!
            navigate('/onboarding');
          }
        } else {
          setErrorMsg(response.message || 'Keycloak authentication failed on the backend.');
        }
      } catch (err: any) {
        setErrorMsg(err.message || 'An unexpected error occurred during Keycloak exchange.');
      }
    };

    authenticateWithKeycloak();
  }, [location, login, navigate]);

  return (
    <div className="flex flex-col items-center justify-center min-h-[80vh] animate-in fade-in">
      <div className="bg-white p-10 rounded-3xl shadow-xl shadow-slate-200/50 border border-slate-100 flex flex-col items-center text-center max-w-sm">
        {errorMsg ? (
          <>
            <div className="w-16 h-16 bg-rose-100 text-rose-600 rounded-full flex items-center justify-center mb-4 shadow-inner">
              <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><path d="m15 9-6 6"/><path d="m9 9 6 6"/></svg>
            </div>
            <h2 className="text-xl font-bold text-slate-800 mb-2">Authentication Error</h2>
            <p className="text-slate-500 mb-8">{errorMsg}</p>
            <button onClick={() => navigate('/login')} className="px-6 py-3 bg-slate-900 text-white rounded-xl font-bold tracking-wide hover:bg-slate-800 transition-colors w-full">
              Return to Login
            </button>
          </>
        ) : (
          <>
            <div className="relative mb-6">
              <div className="absolute inset-0 bg-emerald-100 blur-xl rounded-full opacity-50 animate-pulse"></div>
              <Loader2 className="w-16 h-16 text-emerald-500 animate-spin relative z-10" />
            </div>
            <h2 className="text-2xl font-bold text-slate-800 mb-2">Authenticating</h2>
            <p className="text-slate-500 font-medium">Please wait while we verify your Keycloak credentials...</p>
          </>
        )}
      </div>
    </div>
  );
}
