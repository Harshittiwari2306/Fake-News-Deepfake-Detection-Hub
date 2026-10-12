import { useState, useEffect } from 'react';
import { 
  Clock, Filter, Search, FileText, Image, Video, 
  Mic, CheckCircle, ChevronRight
} from 'lucide-react';
import { api, type AnalysisResult } from '../api/client';

export default function History() {
  const [history, setHistory] = useState<AnalysisResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterType, setFilterType] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedItem, setSelectedItem] = useState<AnalysisResult | null>(null);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    setLoading(true);
    try {
      const data = await api.getHistory(100);
      setHistory(data);
    } catch (err) {
      console.error("Failed to load history:", err);
    } finally {
      setLoading(false);
    }
  };

  const filteredHistory = history.filter((item) => {
    const matchesType = filterType === 'ALL' || item.analysis_type === filterType;
    const matchesSearch = 
      item.prediction.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (item.explanation && item.explanation.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (item.model_name && item.model_name.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesType && matchesSearch;
  });

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'TEXT': return <FileText className="w-4 h-4 text-blue-400" />;
      case 'IMAGE': return <Image className="w-4 h-4 text-purple-400" />;
      case 'VIDEO': return <Video className="w-4 h-4 text-pink-400" />;
      case 'AUDIO': return <Mic className="w-4 h-4 text-cyan-400" />;
      case 'FACTCHECK': return <CheckCircle className="w-4 h-4 text-emerald-400" />;
      default: return <FileText className="w-4 h-4 text-slate-400" />;
    }
  };

  const getRiskBadge = (risk: string) => {
    switch (risk?.toLowerCase()) {
      case 'high':
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-red-500/20 text-red-300 border border-red-500/30">High Risk</span>;
      case 'medium':
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/30">Medium Risk</span>;
      default:
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">Low Risk</span>;
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6 pb-12">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">Analysis & Verification Log</h1>
          <p className="text-slate-400 mt-1">
            Historical audit log of all text scans, image forensics, deepfake clips, and fact checks.
          </p>
        </div>

        <button
          onClick={loadHistory}
          className="self-start sm:self-auto text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3.5 py-2 rounded-xl border border-slate-700 transition-colors flex items-center gap-1.5 cursor-pointer"
        >
          <Clock className="w-3.5 h-3.5" /> Refresh Log
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2 overflow-x-auto w-full md:w-auto pb-2 md:pb-0">
          <Filter className="w-4 h-4 text-slate-500 shrink-0" />
          {['ALL', 'TEXT', 'IMAGE', 'VIDEO', 'AUDIO', 'FACTCHECK'].map((type) => (
            <button
              key={type}
              onClick={() => setFilterType(type)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors shrink-0 cursor-pointer ${
                filterType === type
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-800 text-slate-400 hover:text-white hover:bg-slate-700'
              }`}
            >
              {type}
            </button>
          ))}
        </div>

        <div className="relative w-full md:w-72">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search prediction or reasoning..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* History Items List */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-xl overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-slate-500">
            <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
            Loading audit history...
          </div>
        ) : filteredHistory.length === 0 ? (
          <div className="p-12 text-center text-slate-500 space-y-2">
            <Clock className="w-8 h-8 mx-auto text-slate-600" />
            <p className="font-medium text-slate-400">No records found matching current filter</p>
            <p className="text-xs">Run a text scan or media verification to start populating this log.</p>
          </div>
        ) : (
          <div className="divide-y divide-slate-800">
            {filteredHistory.map((item) => (
              <div
                key={item.id}
                onClick={() => setSelectedItem(item)}
                className="p-4 hover:bg-slate-800/50 transition-colors flex items-center justify-between gap-4 cursor-pointer"
              >
                <div className="flex items-center gap-3.5 min-w-0">
                  <div className="p-2.5 rounded-xl bg-slate-950 border border-slate-800 shrink-0">
                    {getTypeIcon(item.analysis_type)}
                  </div>
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-mono font-medium text-slate-400">#{item.id}</span>
                      <h4 className="text-sm font-semibold text-white truncate">{item.prediction}</h4>
                    </div>
                    <p className="text-xs text-slate-400 truncate mt-0.5">
                      {item.explanation || 'No summary text available.'}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-4 shrink-0">
                  <div className="text-right hidden sm:block">
                    <div className="text-xs font-bold text-white">{item.confidence}% Conf.</div>
                    <div className="text-[10px] text-slate-500">
                      {item.created_at ? new Date(item.created_at).toLocaleDateString() : 'Recent'}
                    </div>
                  </div>
                  {getRiskBadge(item.risk_level)}
                  <ChevronRight className="w-4 h-4 text-slate-600" />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Selected Item Modal Detail */}
      {selectedItem && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-2xl w-full p-6 space-y-4 max-h-[85vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                {getTypeIcon(selectedItem.analysis_type)}
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  {selectedItem.analysis_type} Analysis Detail (#{selectedItem.id})
                </span>
              </div>
              <button
                onClick={() => setSelectedItem(null)}
                className="text-slate-400 hover:text-white text-sm cursor-pointer"
              >
                ✕ Close
              </button>
            </div>

            <div className="space-y-3">
              <h3 className="text-xl font-bold text-white">{selectedItem.prediction}</h3>
              <div className="flex flex-wrap gap-2 items-center">
                {getRiskBadge(selectedItem.risk_level)}
                <span className="text-xs bg-slate-800 text-slate-300 px-2.5 py-1 rounded-md">
                  Confidence: {selectedItem.confidence}%
                </span>
                <span className="text-xs bg-slate-800 text-blue-400 px-2.5 py-1 rounded-md font-mono">
                  {selectedItem.model_name}
                </span>
              </div>
            </div>

            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
              <h5 className="text-xs font-semibold text-slate-400 mb-1">Reasoning & Findings:</h5>
              <p className="text-sm text-slate-200 leading-relaxed">{selectedItem.explanation}</p>
            </div>

            {selectedItem.key_factors && selectedItem.key_factors.length > 0 && (
              <div>
                <h5 className="text-xs font-semibold text-slate-400 mb-2">Key Factors Identified:</h5>
                <ul className="space-y-1.5">
                  {selectedItem.key_factors.map((f, i) => (
                    <li key={i} className="text-xs text-slate-300 flex items-start gap-2">
                      <span className="text-blue-400 font-bold">•</span>
                      <span>{f}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
