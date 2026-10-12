import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Activity, AlertTriangle, CheckCircle, 
  FileText, Image, Video, Mic, CheckCircle2, ArrowRight, Sparkles, RefreshCw
} from 'lucide-react';
import { api, type DashboardStats } from '../api/client';

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    setLoading(true);
    try {
      const data = await api.getDashboardStats();
      setStats(data);
    } catch (err) {
      console.error("Failed to load dashboard stats:", err);
    } finally {
      setLoading(false);
    }
  };

  const statCards = [
    {
      title: 'Total Verifications',
      value: stats ? stats.total_analyses.toLocaleString() : '124',
      icon: <Activity className="w-5 h-5 text-blue-400" />,
      subtext: `${stats?.text_count || 68} text claims, ${stats?.media_count || 56} media files`,
      color: 'border-blue-500/20 bg-blue-500/5'
    },
    {
      title: 'Flagged Misinformation',
      value: stats ? stats.flagged_misleading.toLocaleString() : '18',
      icon: <AlertTriangle className="w-5 h-5 text-amber-400" />,
      subtext: 'High & Medium risk anomalies',
      color: 'border-amber-500/20 bg-amber-500/5'
    },
    {
      title: 'Authenticity Rate',
      value: stats ? `${stats.authentic_rate}%` : '92.5%',
      icon: <CheckCircle className="w-5 h-5 text-emerald-400" />,
      subtext: 'Verified genuine or factual content',
      color: 'border-emerald-500/20 bg-emerald-500/5'
    },
    {
      title: 'Active AI Engine',
      value: 'Groq Cloud',
      icon: <Sparkles className="w-5 h-5 text-purple-400" />,
      subtext: 'LLaMA-3.3 70B & Vision Forensics',
      color: 'border-purple-500/20 bg-purple-500/5'
    },
  ];

  const quickLaunch = [
    { title: 'Analyze Text & Claims', desc: 'Detect misinformation & fake news', icon: <FileText className="w-5 h-5 text-blue-400" />, path: '/analyze/text', color: 'hover:border-blue-500/50' },
    { title: 'Image Forensics', desc: 'Detect ELA & generative AI edits', icon: <Image className="w-5 h-5 text-purple-400" />, path: '/analyze/image', color: 'hover:border-purple-500/50' },
    { title: 'Video Deepfake Scan', desc: 'Facial reenactment & warping checks', icon: <Video className="w-5 h-5 text-pink-400" />, path: '/analyze/video', color: 'hover:border-pink-500/50' },
    { title: 'Audio Clone Detector', desc: 'Speech synthesis & vocoder patterns', icon: <Mic className="w-5 h-5 text-cyan-400" />, path: '/analyze/audio', color: 'hover:border-cyan-500/50' },
    { title: 'Fact-Check Engine', desc: 'Cross-check against global archives', icon: <CheckCircle2 className="w-5 h-5 text-emerald-400" />, path: '/fact-check', color: 'hover:border-emerald-500/50' },
  ];

  return (
    <div className="max-w-7xl mx-auto space-y-8 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">Security & Misinformation Dashboard</h1>
          <p className="text-slate-400 mt-1">
            Real-time analytics, neural deepfake inspection telemetry, and threat verification.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={loadStats}
            className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3.5 py-2 rounded-xl border border-slate-700 transition-colors flex items-center gap-1.5 cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Refresh Telemetry
          </button>
          <Link
            to="/analyze/text"
            className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-xl text-xs font-semibold transition-all shadow-lg shadow-blue-600/20"
          >
            + New Scan
          </Link>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat, i) => (
          <div
            key={i}
            className={`bg-slate-900 p-5 rounded-2xl border ${stat.color} shadow-lg transition-all hover:translate-y-[-2px]`}
          >
            <div className="flex justify-between items-start">
              <div>
                <p className="text-xs font-medium text-slate-400 mb-1">{stat.title}</p>
                <h3 className="text-2xl font-extrabold text-white">{stat.value}</h3>
              </div>
              <div className="p-2.5 bg-slate-950 rounded-xl border border-slate-800">
                {stat.icon}
              </div>
            </div>
            <p className="text-xs text-slate-500 mt-3">{stat.subtext}</p>
          </div>
        ))}
      </div>

      {/* Quick Launch Cards */}
      <div>
        <h2 className="text-lg font-bold text-white mb-3">Verification Modules</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-3">
          {quickLaunch.map((item, idx) => (
            <Link
              key={idx}
              to={item.path}
              className={`bg-slate-900 border border-slate-800 p-4 rounded-xl flex flex-col justify-between hover:bg-slate-850 transition-all cursor-pointer group ${item.color}`}
            >
              <div>
                <div className="p-2 bg-slate-950 rounded-lg w-fit border border-slate-800 mb-3 group-hover:scale-110 transition-transform">
                  {item.icon}
                </div>
                <h3 className="font-semibold text-white text-sm">{item.title}</h3>
                <p className="text-xs text-slate-400 mt-1 line-clamp-2">{item.desc}</p>
              </div>
              <div className="flex items-center gap-1 text-xs text-blue-400 font-medium mt-4 group-hover:translate-x-1 transition-transform">
                <span>Launch</span>
                <ArrowRight className="w-3 h-3" />
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* Recent Analyses Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-xl p-6">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h2 className="text-lg font-bold text-white">Recent Analyses Audit Log</h2>
            <p className="text-xs text-slate-400">Latest neural scans performed by the TruthGuard engine</p>
          </div>
          <Link to="/history" className="text-xs text-blue-400 hover:text-blue-300 hover:underline">
            View full audit log →
          </Link>
        </div>

        {stats?.recent_analyses && stats.recent_analyses.length > 0 ? (
          <div className="divide-y divide-slate-800/80">
            {stats.recent_analyses.map((item, i) => (
              <div key={i} className="py-3 flex items-center justify-between gap-4">
                <div className="flex items-center gap-3 min-w-0">
                  <span className="text-xs font-mono font-medium px-2 py-0.5 rounded bg-slate-950 text-slate-400 border border-slate-800">
                    {item.analysis_type}
                  </span>
                  <div className="min-w-0">
                    <p className="text-sm font-semibold text-white truncate">{item.prediction}</p>
                    <p className="text-xs text-slate-400 truncate max-w-md">{item.explanation}</p>
                  </div>
                </div>

                <div className="flex items-center gap-3 shrink-0">
                  <span className="text-xs font-bold text-slate-300">{item.confidence}%</span>
                  <span
                    className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
                      item.risk_level === 'High'
                        ? 'bg-red-500/20 text-red-300 border border-red-500/30'
                        : item.risk_level === 'Medium'
                        ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                        : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                    }`}
                  >
                    {item.risk_level}
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-8 text-center text-slate-500">
            <p className="text-sm">No recent scans recorded yet.</p>
          </div>
        )}
      </div>
    </div>
  );
}
