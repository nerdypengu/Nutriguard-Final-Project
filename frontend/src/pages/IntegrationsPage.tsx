import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../utils/api';
import { MessageSquare, Save, CheckCircle2, AlertCircle, ExternalLink, ShieldAlert } from 'lucide-react';

export default function IntegrationsPage() {
  const { user, login } = useAuth();
  const [discordId, setDiscordId] = useState('');
  const [discordUsername, setDiscordUsername] = useState('');
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  useEffect(() => {
    if (user) {
      setDiscordId(user.discord_id || '');
      setDiscordUsername(user.discord_username || '');
    }
  }, [user]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;
    
    setSaving(true);
    setMessage({ type: '', text: '' });

    try {
      const profileRes = await api.put(`/users/${user.id}`, {
        discord_id: discordId || null,
        discord_username: discordUsername || null
      });

      if (!profileRes.success) throw new Error('Gagal update integrasi Discord');

      const token = localStorage.getItem('access_token') || '';
      login({ ...user, discord_id: discordId, discord_username: discordUsername }, token);

      setMessage({ type: 'success', text: 'Konfigurasi Discord berhasil disimpan!' });
    } catch (error) {
      setMessage({ type: 'error', text: error instanceof Error ? error.message : 'Terjadi kesalahan saat menyimpan.' });
    } finally {
      setSaving(false);
      setTimeout(() => setMessage({ type: '', text: '' }), 5000);
    }
  };

  const isConnected = !!(user?.discord_id || user?.discord_username);

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in duration-500">
      <div>
        <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Discord Bot NutriGuard</h1>
        <p className="text-slate-500 mt-1">Kelola koneksi Discord untuk mencatat makanan langsung lewat chat.</p>
      </div>

      {message.text && (
        <div className={`p-4 rounded-xl flex items-center gap-3 animate-in fade-in ${message.type === 'success' ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-rose-50 text-rose-800 border border-rose-200'}`}>
          {message.type === 'success' ? <CheckCircle2 className="w-5 h-5 text-emerald-500" /> : <AlertCircle className="w-5 h-5 text-rose-500" />}
          <p className="font-medium">{message.text}</p>
        </div>
      )}

      <div className="bg-white rounded-3xl p-8 shadow-sm border border-slate-100 overflow-hidden relative">
        <div className="absolute top-0 right-0 -mx-8 -my-8 w-64 h-64 bg-[#5865F2]/5 rounded-full blur-3xl pointer-events-none"></div>

        <div className="flex flex-col md:flex-row gap-8 items-start relative z-10">
          <div className="w-20 h-20 bg-[#5865F2]/10 rounded-2xl flex items-center justify-center shrink-0 border border-[#5865F2]/20">
            <MessageSquare className="w-10 h-10 text-[#5865F2]" />
          </div>

          <div className="flex-1 space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-slate-900 flex items-center gap-3">
                Koneksi Discord
                {isConnected && (
                  <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-700 text-xs font-bold uppercase tracking-wide">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Terhubung
                  </span>
                )}
              </h2>
              <p className="text-slate-600 mt-2 leading-relaxed">
                Sinkronkan akun Discord Anda agar Anda dapat langsung mencatat makanan melalui server Discord. AI kami akan memproses setiap pesan yang Anda kirim ke bot dan menghitung asupan kalori Anda secara otomatis.
              </p>
            </div>

            <div className="bg-slate-50 border border-slate-200 rounded-2xl p-5 flex items-start gap-4">
              <ShieldAlert className="w-5 h-5 text-amber-500 shrink-0 mt-0.5" />
              <div>
                <h4 className="text-sm font-bold text-slate-900 mb-1">Status Koneksi</h4>
                {isConnected ? (
                  <p className="text-sm text-slate-600">
                    Akun Anda saat ini siap menerima data dari Discord User: <span className="font-mono bg-slate-200 px-1.5 py-0.5 rounded text-slate-800">{user?.discord_username || 'Unknown'}</span>
                  </p>
                ) : (
                  <p className="text-sm text-slate-600">Belum ada akun Discord yang diotorisasi. NutriGuard bot tidak dapat memonitor pesan Anda.</p>
                )}
              </div>
            </div>

            <div className="p-4 bg-indigo-50 rounded-xl border border-indigo-100">
              <p className="text-sm text-indigo-800 font-medium">
                Untuk menggunakan Discord Bot, ikuti langkah berikut:
                <br/><br/>
                <b>1.</b> Isi <strong>Discord Username</strong> dan <strong>Discord ID</strong> Anda di kotak di bawah ini, lalu klik <strong>Simpan Pengaturan</strong>.
                <br/>
                <b>2.</b> Klik tombol di bawah untuk menyinkronkan dan mengizinkan bot di server Anda.
              </p>
              <a 
                href="https://discord.com/oauth2/authorize?client_id=1489137371239813150" 
                target="_blank" 
                rel="noopener noreferrer"
                className="mt-4 inline-flex items-center justify-center gap-2 px-6 py-2.5 bg-[#5865F2] hover:bg-[#4752C4] text-white text-sm font-semibold rounded-xl shadow-sm transition-all"
              >
                Sync Discord Account
                <ExternalLink className="w-4 h-4" />
              </a>
            </div>

            <form onSubmit={handleSave} className="space-y-4 pt-4 border-t border-slate-100">
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">Discord Username</label>
                <input
                  type="text"
                  value={discordUsername}
                  onChange={(e) => setDiscordUsername(e.target.value)}
                  className="w-full md:w-2/3 px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 font-medium text-slate-800"
                  placeholder="Misal: abcd#1234 atau abcd"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">Discord ID</label>
                <input
                  type="text"
                  value={discordId}
                  onChange={(e) => setDiscordId(e.target.value)}
                  className="w-full md:w-2/3 px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 font-medium text-slate-800"
                  placeholder="Misal: 123456789012345678"
                />
                <p className="text-xs text-slate-500 mt-2">Cara mendapatkan Discord ID: Aktifkan Developer Mode di Settings Discord &gt; Klik kanan profil &gt; Copy User ID.</p>
              </div>

              <button
                type="submit"
                disabled={saving}
                className="flex items-center justify-center gap-2 py-3 px-6 mt-4 border border-transparent rounded-xl shadow-sm text-sm font-bold text-white bg-emerald-600 hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 disabled:opacity-70 transition-all"
              >
                <Save className="w-4 h-4" />
                {saving ? 'Menyimpan...' : 'Simpan Pengaturan'}
              </button>
            </form>

          </div>
        </div>
      </div>
    </div>
  );
}
