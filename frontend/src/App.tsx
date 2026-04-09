import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout } from './components/Layout';
import { TopBarLayout } from './components/TopBarLayout';
import { ProtectedRoute } from './components/ProtectedRoute';
import { AuthProvider } from './context/AuthContext';

import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import KeycloakCallback from './pages/KeycloakCallback';
import OnboardingPage from './pages/OnboardingPage';
import DashboardPage from './pages/DashboardPage';
import FoodLogPage from './pages/FoodLogPage';
import SearchPage from './pages/SearchPage';
import IntegrationsPage from './pages/IntegrationsPage';
import ProfilePage from './pages/ProfilePage';
import MealChatPage from './pages/MealChatPage';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Public Pages with Top Bar */}
          <Route element={<TopBarLayout />}>
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<LoginPage />} />
             <Route path="/signup" element={<SignupPage />} />
             <Route path="/auth/callback" element={<KeycloakCallback />} />
          </Route>

          {/* Protected Pages */}
          <Route element={<ProtectedRoute />}>
             {/* Splash pages under protected but without sidebar layout */}
             <Route path="/onboarding" element={<OnboardingPage />} />

            {/* Main App with Sidebar */}
            <Route element={<Layout />}>
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/log" element={<FoodLogPage />} />
              <Route path="/search" element={<SearchPage />} />
              <Route path="/integrations" element={<IntegrationsPage />} />
              <Route path="/profile" element={<ProfilePage />} />
              <Route path="/meal-chat" element={<MealChatPage />} />
            </Route>
          </Route>
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;