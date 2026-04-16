import { createClient } from '@supabase/supabase-js';

// Get these from env
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || '';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || '';

if (!supabaseUrl || !supabaseAnonKey) {
  console.warn('Supabase credentials not fully configured in frontend environment.');
}

// We must pass valid URLs to createClient, otherwise it throws and crashes the app
export const realtimeSupabase = (supabaseUrl && supabaseAnonKey) 
  ? createClient(supabaseUrl, supabaseAnonKey, {
      auth: {
        persistSession: false // We use Keycloak for persistence, not Supabase
      },
      realtime: {
        params: {
          eventsPerSecond: 10,
        },
      },
    })
  : null;

export const setupRealtimeAuth = (customToken: string) => {
  if (realtimeSupabase) {
    realtimeSupabase.realtime.setAuth(customToken);
  }
};
