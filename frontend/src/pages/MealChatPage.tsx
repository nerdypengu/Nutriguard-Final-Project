import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../utils/api';
import {
  MessageSquare,
  Send,
  Loader2,
  XCircle,
  History
} from 'lucide-react';

interface NutritionResult {
  [key: string]: any;
}

interface JobStatus {
  id: string;
  status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED' | 'CANCELLED';
  progress_message: string;
  message?: string;
  prompt?: string;
  content?: string;
  result: NutritionResult | null;
  created_at: string;
  updated_at: string;
}

export default function MealChatPage() {
  const { user } = useAuth();
  const [message, setMessage] = useState('');
  const [jobStatus, setJobStatus] = useState<JobStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<JobStatus[]>([]);
  const [isPolling, setIsPolling] = useState(false);

  // Fetch job history on mount
  useEffect(() => {
    if (user?.id) {
      fetchHistory();
    }
  }, [user]);

  const fetchHistory = async () => {
    try {
      const response = await api.get(`/meal-processing/jobs?limit=10`);
      if (response && response.jobs) {
        setHistory(response.jobs);
      }
    } catch (err: any) {
      console.error('Failed to fetch history', err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim() || !user?.id) return;

    setLoading(true);
    setError(null);
    setJobStatus({
      id: "temp",
      status: "PENDING",
      progress_message: "Mengirim pesan...",
      message: message.trim(),
      content: message.trim(),
      result: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    });

    try {
      const response = await api.post('/meal-processing/chat', {
        user_id: user.id,
        message: message.trim()
      });

      setMessage('');
      setJobStatus(prev => prev ? {
        ...prev,
        id: response.job_id,
        message: message.trim(),
        content: message.trim(),
        status: response.status || 'PENDING',
        progress_message: response.message || 'Pesanan diterima, AI mulai bekerja...'
      } : null);

      pollStatus(response.job_id);
    } catch (err: any) {
      setError(err.message || 'Gagal mengirim pesan');
      setLoading(false);
      setJobStatus(null);
    }
  };

  const pollStatus = (id: string) => {
    setIsPolling(true);
    const pollInterval = setInterval(async () => {
      try {
        const data = await api.get(`/meal-processing/status/${id}`);
        setJobStatus(data);

        if (['COMPLETED', 'FAILED', 'CANCELLED'].includes(data.status)) {
          clearInterval(pollInterval);
          setIsPolling(false);
          setLoading(false);
          // Refresh history if completed
          if (data.status === 'COMPLETED') {
            fetchHistory();
          }
        }
      } catch (err: any) {
        console.error('Polling error:', err);
        clearInterval(pollInterval);
        setError('Koneksi terputus saat mengecek status');
        setIsPolling(false);
        setLoading(false);
      }
    }, 2000);
  };

  const getResultText = (result: any): string => {
    if (!result) return "";
    const textContent = typeof result === 'string'
      ? result
      : (result?.text || result?.answer || result?.content || result?.message || result?.result || (result ? Object.values(result)[0] : ''));
    return typeof textContent === 'string' ? String(textContent) : JSON.stringify(result);
  };

  const renderResult = (result: any) => {
    return (
      <div className="text-slate-800 whitespace-pre-wrap leading-relaxed text-[15px]">
        {getResultText(result)}
      </div>
    );
  };

  return (
    <div className="flex flex-col md:flex-row h-[calc(100vh-8rem)] gap-6 w-full max-w-6xl mx-auto">
      {/* Sidebar for History */}
      <div className="w-full md:w-72 lg:w-80 flex-shrink-0 flex flex-col h-[30vh] md:h-full bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-100 bg-slate-50/50">
          <h3 className="font-semibold text-slate-700 flex items-center gap-2">
            <History className="w-5 h-5 text-emerald-600" />
            Riwayat Terakhir
          </h3>
        </div>
        <div className="flex-1 overflow-y-auto p-3 space-y-2 bg-slate-50/30">
          {history.length > 0 ? (
            history.map((job) => (
              <div key={job.id}
                className={`p-3 rounded-xl border text-sm cursor-pointer transition-all ${jobStatus?.id === job.id
                  ? 'bg-emerald-50 border-emerald-300 shadow-sm'
                  : 'bg-white border-slate-200 hover:border-emerald-300 hover:shadow-sm'
                  }`}
                onClick={() => setJobStatus(job)}
              >
                <div className="mb-2">
                  <p className="font-bold text-slate-800 line-clamp-2 leading-relaxed">
                    {job.content || job.message || job.prompt || (job.result && getResultText(job.result)) || "Sesi Obrolan..."}
                  </p>
                </div>
                <div className="flex items-center gap-1.5 text-xs text-slate-500">
                  {['PENDING', 'PROCESSING'].includes(job.status) && <Loader2 className="w-3.5 h-3.5 text-emerald-500 animate-spin" />}
                  {job.status === 'FAILED' && <XCircle className="w-3.5 h-3.5 text-rose-500" />}
                  <span className="line-clamp-1 italic">{job.progress_message || job.status}</span>
                </div>
              </div>
            ))
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-slate-400 p-4 text-center space-y-2">
              <History className="w-8 h-8 opacity-20" />
              <p className="text-sm">Belum ada riwayat percakapan</p>
            </div>
          )}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col h-full bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 md:p-6 pb-4 border-b border-slate-100 bg-slate-50/30">
          <h1 className="text-xl md:text-2xl font-bold tracking-tight text-slate-900 flex items-center gap-3">
            <div className="p-2 bg-emerald-100 rounded-xl text-emerald-600">
              <MessageSquare className="w-5 h-5" />
            </div>
            Tanya AI Kami
          </h1>
          <p className="text-slate-500 mt-2 text-sm md:text-base">
            Ceritakan apa yang kamu makan, atau tanya apapun seputar nutrisi.
          </p>
        </div>

        <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-6 flex flex-col-reverse bg-slate-50/10">
          {/* Current Job Display format chat */}
          {jobStatus && (
            <div className="flex flex-col gap-6 w-full pb-4">
              {/* User Bubble */}
              {(jobStatus.content || jobStatus.message || jobStatus.prompt) && (
                <div className="flex justify-end w-full">
                  <div className="max-w-[85%] md:max-w-[75%] bg-emerald-600 text-white px-5 py-3.5 rounded-3xl rounded-tr-sm shadow-sm relative">
                    <p className="whitespace-pre-wrap leading-relaxed text-[15px]">{jobStatus.content || jobStatus.message || jobStatus.prompt}</p>
                  </div>
                </div>
              )}

              {/* AI Bubble */}
              <div className="flex justify-start w-full">
                <div className="max-w-[90%] md:max-w-[85%] bg-white border border-slate-200 text-slate-700 px-5 py-4 rounded-3xl rounded-tl-sm shadow-sm relative">
                  {['PENDING', 'PROCESSING'].includes(jobStatus.status) ? (
                    <div className="flex items-center gap-3 text-emerald-600">
                      <Loader2 className="w-5 h-5 animate-spin" />
                      <span className="font-medium text-sm animate-pulse">{jobStatus.progress_message}</span>
                    </div>
                  ) : jobStatus.status === 'FAILED' ? (
                    <div className="flex items-center gap-3 text-rose-600">
                      <XCircle className="w-5 h-5" />
                      <span className="font-medium text-sm">{jobStatus.progress_message}</span>
                    </div>
                  ) : jobStatus.status === 'COMPLETED' && jobStatus.result ? (
                    renderResult(jobStatus.result)
                  ) : (
                    <div className="flex items-center gap-3 text-slate-500">
                      <span className="font-medium text-sm">{jobStatus.progress_message}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Start info when no current job */}
          {!jobStatus && (
            <div className="text-center p-10 bg-slate-50 rounded-2xl border border-slate-100 mb-auto mt-10 text-slate-500 shadow-sm">
              <MessageSquare className="w-12 h-12 mx-auto mb-4 text-emerald-200" />
              <p className="font-medium text-slate-700">Mulai chat dengan AI</p>
              <p className="text-sm mt-2 text-slate-500">Coba ketik:</p>
              <p className="text-sm mt-1 italic text-slate-500 bg-white inline-block px-3 py-1 rounded-full border border-slate-200">"Saya sarapan bubur ayam dan teh manis"</p>
            </div>
          )}

          {/* Error overlay */}
          {error && (
            <div className="p-4 bg-rose-50 border border-rose-200 text-rose-700 rounded-xl flex items-center gap-2">
              <XCircle className="w-5 h-5" />
              {error}
            </div>
          )}
        </div>

        <div className="p-4 md:p-6 border-t border-slate-100 bg-white">
          <form onSubmit={handleSubmit} className="flex gap-2">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Ketik detail makananmu di sini..."
              disabled={loading || isPolling}
              className="flex-1 bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 focus:bg-white shadow-sm disabled:bg-slate-100 disabled:text-slate-500 transition-all"
            />
            <button
              type="submit"
              disabled={loading || isPolling || !message.trim()}
              className="bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-200 disabled:text-slate-400 text-white px-6 py-3 rounded-xl font-medium shadow-sm transition-all flex items-center gap-2"
            >
              {loading || isPolling ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  <span className="hidden sm:inline">Kirim</span>
                  <Send className="w-5 h-5" />
                </>
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
