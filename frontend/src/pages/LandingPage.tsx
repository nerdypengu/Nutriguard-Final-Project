import { ArrowRight, MessageSquare, Bot, LineChart, Sparkles } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function LandingPage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[80vh] animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="text-center max-w-3xl mb-16">
        <div className="inline-flex items-center gap-2 px-3 py-1 mb-6 rounded-full bg-emerald-100 text-emerald-800 text-sm font-medium">
          <Sparkles className="w-4 h-4" />
          <span>Cara baru melacak nutrisi</span>
        </div>
        <h1 className="text-5xl md:text-6xl font-extrabold text-slate-900 tracking-tight mb-6 leading-tight">
          Lacak Kalori Anda Semudah Mengirim Pesan di <span className="text-[#5865F2]">Discord</span>
        </h1>
        <p className="text-xl text-slate-600 mb-10 leading-relaxed max-w-2xl mx-auto">
          NutriGuard adalah asisten nutrisi berbasis AI. Tidak perlu lagi input manual yang rumit. Cukup ketik apa yang Anda makan di Discord, dan biarkan AI kami yang mengaturnya.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link 
            to="/login"
            className="inline-flex items-center justify-center gap-2 bg-emerald-600 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:bg-emerald-700 hover:shadow-lg hover:shadow-emerald-200 transition-all duration-300 transform hover:-translate-y-1"
          >
            Mulai Sekarang
            <ArrowRight className="w-5 h-5" />
          </Link>
          <button className="inline-flex items-center justify-center gap-2 bg-white text-slate-700 border border-slate-200 px-8 py-4 rounded-xl font-semibold text-lg hover:bg-slate-50 hover:border-slate-300 transition-all duration-300">
            Pelajari Lebih Lanjut
          </button>
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-8 w-full max-w-5xl mt-8">
        <div className="bg-white p-8 rounded-3xl shadow-sm border border-slate-100 hover:shadow-md hover:border-emerald-100 transition-all duration-300 group">
          <div className="w-14 h-14 bg-blue-50 text-blue-600 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
            <Bot className="w-7 h-7" />
          </div>
          <h3 className="text-xl font-bold text-slate-900 mb-3">AI Tracking</h3>
          <p className="text-slate-600 leading-relaxed">
            Teknologi AI kami secara otomatis mengenali makanan dan porsi dari teks Anda, lalu menghitung kalori dengan akurat.
          </p>
        </div>

        <div className="bg-white p-8 rounded-3xl shadow-sm border border-slate-100 hover:shadow-md hover:border-emerald-100 transition-all duration-300 group">
          <div className="w-14 h-14 bg-[#5865F2]/10 text-[#5865F2] rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
            <MessageSquare className="w-7 h-7" />
          </div>
          <h3 className="text-xl font-bold text-slate-900 mb-3">Seamless Discord</h3>
          <p className="text-slate-600 leading-relaxed">
            Integrasi langsung dengan server Discord Anda. Laporkan makanan harian bersama teman-teman komunitas gamer Anda.
          </p>
        </div>

        <div className="bg-white p-8 rounded-3xl shadow-sm border border-slate-100 hover:shadow-md hover:border-emerald-100 transition-all duration-300 group">
          <div className="w-14 h-14 bg-emerald-50 text-emerald-600 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
            <LineChart className="w-7 h-7" />
          </div>
          <h3 className="text-xl font-bold text-slate-900 mb-3">Personalized Plans</h3>
          <p className="text-slate-600 leading-relaxed">
            Dapatkan rekomendasi target kalori dan makronutrisi harian yang disesuaikan dengan profil dan tujuan kesehatan Anda.
          </p>
        </div>
      </div>
    </div>
  );
}
