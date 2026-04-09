import { useState } from 'react';
import { MessageSquare, RefreshCw, CheckCircle2, ShieldAlert } from 'lucide-react';

export default function IntegrationsPage() {
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);

  const handleConnect = () => {
    setIsConnecting(true);
    setTimeout(() => {
      setIsConnecting(false);
      setIsConnected(true);
    }, 1500);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in duration-500">
      <div>
        <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Integrasi Aplikasi</h1>
        <p className="text-slate-500 mt-1">Kelola koneksi aplikasi pihak ketiga untuk pengalaman tracking tanpa hambatan.</p>
      </div>

      <div className="bg-white rounded-3xl p-8 shadow-sm border border-slate-100 overflow-hidden relative">
        {/* Background blobs for visual flair */}
        <div className="absolute top-0 right-0 -mx-8 -my-8 w-64 h-64 bg-[#5865F2]/5 rounded-full blur-3xl pointer-events-none"></div>

        <div className="flex flex-col md:flex-row gap-8 items-start relative z-10">
          <div className="w-20 h-20 bg-[#5865F2]/10 rounded-2xl flex items-center justify-center shrink-0 border border-[#5865F2]/20">
            <MessageSquare className="w-10 h-10 text-[#5865F2]" />
          </div>

          <div className="flex-1 space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-slate-900 flex items-center gap-3">
                Discord Bot NutriGuard
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
                    Akun Anda saat ini terhubung dengan Discord User: <span className="font-mono bg-slate-200 px-1.5 py-0.5 rounded text-slate-800">RakaGamer#1234</span>
                  </p>
                ) : (
                  <p className="text-sm text-slate-600">Belum ada akun Discord yang diotorisasi. NutriGuard bot tidak dapat memonitor pesan Anda.</p>
                )}
              </div>
            </div>

            <div className="pt-4 border-t border-slate-100 flex items-center gap-4">
              {!isConnected ? (
                <button
                  onClick={handleConnect}
                  disabled={isConnecting}
                  className="flex items-center justify-center gap-3 bg-[#5865F2] hover:bg-[#4752C4] text-white px-8 py-4 rounded-xl font-bold text-lg transition-all shadow-md shadow-[#5865F2]/20 disabled:opacity-70 disabled:cursor-wait"
                >
                  {isConnecting ? (
                    <RefreshCw className="w-6 h-6 animate-spin" />
                  ) : (
                    <MessageSquare className="w-6 h-6" />
                  )}
                  {isConnecting ? 'Menghubungkan...' : 'Otorisasi Bot NutriGuard'}
                </button>
              ) : (
                <button
                  onClick={() => setIsConnected(false)}
                  className="flex items-center justify-center gap-2 bg-white text-rose-600 border border-rose-200 hover:bg-rose-50 px-6 py-3 rounded-xl font-bold transition-all"
                >
                  Putuskan Koneksi
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
