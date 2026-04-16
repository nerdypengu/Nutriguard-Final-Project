import { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import Keycloak from 'keycloak-js';
import { api } from '../utils/api';

export interface User {
  id: string;
  email: string;
  discord_id?: string;
  discord_username?: string;
  is_subscribed?: boolean;
}

interface AuthContextType {
  isAuthenticated: boolean;
  user: User | null;
  login: (userData: User, token: string) => void;
  logout: () => void;
  keycloakLogin: () => void;
  keycloakRegister: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

const keycloak = new Keycloak({
  url: import.meta.env.VITE_KEYCLOAK_URL || 'http://localhost:8080',
  realm: import.meta.env.VITE_KEYCLOAK_REALM || 'nutriguard',
  clientId: import.meta.env.VITE_KEYCLOAK_CLIENT_ID || 'nutriguard-frontend',
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isInitializing, setIsInitializing] = useState<boolean>(true);

  useEffect(() => {
    const initAuth = async () => {
      try {
        const authenticated = await keycloak.init({ 
          onLoad: 'check-sso',
          checkLoginIframe: false,
        });

        if (authenticated && keycloak.token) {
          localStorage.setItem('access_token', keycloak.token);
          
          if (keycloak.idTokenParsed?.email) {
             const email = keycloak.idTokenParsed.email;
             try {
                const userRes = await api.get(`/users/email/${encodeURIComponent(email)}`);
                if (userRes && userRes.success && userRes.data) {
                   setUser(userRes.data);
                } else if (userRes && userRes.id) {
                   setUser(userRes);
                } else {
                   setUser({ id: keycloak.subject || '', email });
                }
             } catch(err) {
                console.error("Failed to fetch user from backend, using basic profile", err);
                setUser({ id: keycloak.subject || '', email });
             }
          }
          setIsAuthenticated(true);
        } else {
          // Standard local auth fallback
          const storedToken = localStorage.getItem('access_token');
          const storedUser = localStorage.getItem('user');

          if (storedToken && storedUser) {
            setUser(JSON.parse(storedUser));
            setIsAuthenticated(true);
          }
        }
      } catch (e) {
        console.error('Failed to initialize Keycloak', e);
      } finally {
        setIsInitializing(false);
      }
    };

    initAuth();
  }, []);

  const login = (userData: User, token: string) => {
    localStorage.setItem('access_token', token);
    localStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);
    setIsAuthenticated(true);
  };

  const logout = () => {
    if (keycloak.authenticated) {
       keycloak.logout().then(() => {
          localStorage.removeItem('access_token');
          localStorage.removeItem('user');
          setUser(null);
          setIsAuthenticated(false);
       });
    } else {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      setUser(null);
      setIsAuthenticated(false);
    }
  };

  const keycloakLogin = () => keycloak.login();
  const keycloakRegister = () => keycloak.register();

  if (isInitializing) {
    return (
       <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-emerald-500"></div>
       </div>
    );
  }

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, login, logout, keycloakLogin, keycloakRegister }}>
      {children}
    </AuthContext.Provider>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
}
