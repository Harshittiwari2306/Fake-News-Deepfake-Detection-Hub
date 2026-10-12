import { useState } from 'react';
import { 
  Search, ExternalLink, 
  ShieldCheck, AlertTriangle, XCircle, Sparkles, RefreshCw, BookOpen
} from 'lucide-react';
import { api, type FactCheckResponse } from '../api/client';

export default function FactCheck() {
  const [claim, setClaim] = useState('');
  const [context, setContext] = useState('');
  const [isVerifying, setIsVerifying] = useState(false);
  const [result, setResult] = useState<FactCheckResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const sampleClaims = [
    "The Great Wall of China is the only human-made structure visible from space with the naked eye.",
    "Humans only use 10 percent of their total brain capacity.",
    "Drinking 8 glasses of pure lemon water daily cures cancer completely.",
    "The James Webb Space Telescope detected water vapor in the atmosphere of an exoplanet."
  ];

  const handleFactCheck = async () => {
    if (!claim.trim()) return;
    setIsVerifying(true);
    setError(null);
    setResult(null);

    try {
      const data = await api.factCheck({
        claim,
        context: context.trim() || undefined,
      });
      setResult(data);
    } catch (err: any) {
      console.error(err);
      setError(err?.response?.data?.detail || "Failed to cross-check claim. Please verify backend.");
    } finally {
      setIsVerifying(false);
    }
  };

  const getVerdictStyle = (verdict: string) => {
    const v = verdict.toLowerCase();
    if (v.includes('true') || v.includes('verified true')) {
      return {
        bg: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400',
        badge: 'bg-emerald-600 text-white',
        icon: <ShieldCheck className="w-5 h-5 text-emerald-400" />
      };
    } else if (v.includes('false') || v.includes('fabricated')) {
      return {
        bg: 'bg-red-500/10 border-red-500/30 text-red-400',
        badge: 'bg-red-600 text-white',
        icon: <XCircle className="w-5 h-5 text-red-400" />
      };
    } else {
      return {
        bg: 'bg-amber-500/10 border-amber-500/30 text-amber-400',
        badge: 'bg-amber-600 text-white',
        icon: <AlertTriangle className="w-5 h-5 text-amber-400" />
      };
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8 pb-12">
      <div>
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold uppercase tracking-wider mb-2">
          <Sparkles className="w-3.5 h-3.5" /> Groq Neural Fact Verification
        </div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight">Authoritative Fact-Checking Engine</h1>
        <p className="text-slate-400 mt-1">
          Cross-check viral rumors and controversial assertions against journalistic consensus and global fact-checking archives.
        </p>
      </div>

      {/* Preset claim buttons */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4">
        <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
          ⚡ Try Fact-Checking Famous Claims:
        </p>
        <div className="flex flex-wrap gap-2">
          {sampleClaims.map((sample, idx) => (
            <button
              key={idx}
              onClick={() => setClaim(sample)}
              className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white px-3 py-1.5 rounded-lg border border-slate-700/60 transition-all text-left cursor-pointer"
            >
              "{sample.slice(0, 50)}..."
            </button>
          ))}
        </div>
      </div>

      {/* Input Form */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-xl p-6 space-y-4">
        <div>
          <label className="block text-xs font-medium text-slate-400 mb-1">Claim / Statement to Verify *</label>
          <input
            type="text"
            className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
            placeholder="e.g. World Health Organization officially declared climate change a viral pathogen..."
            value={claim}
            onChange={(e) => setClaim(e.target.value)}
          />
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-400 mb-1">Additional Context or Where You Saw It (Optional)</label>
          <textarea
            rows={2}
            className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all resize-none"
            placeholder="e.g. Circulating on TikTok and Facebook groups with 50k shares..."
            value={context}
            onChange={(e) => setContext(e.target.value)}
          />
        </div>

        {error && (
          <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
            {error}
          </div>
        )}

        <div className="flex justify-end pt-2">
          <button
            onClick={handleFactCheck}
            disabled={isVerifying || !claim.trim()}
            className={`flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl font-medium text-white transition-all shadow-lg ${
              isVerifying || !claim.trim()
                ? 'bg-blue-600/50 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-500 shadow-blue-600/20 hover:shadow-blue-600/40 cursor-pointer active:scale-95'
            }`}
          >
            {isVerifying ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Cross-referencing Global Fact Archives...</span>
              </>
            ) : (
              <>
                <Search className="w-4 h-4" />
                <span>Verify Claim with Groq</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Results */}
      {result && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-300">
          <div className="p-6 border-b border-slate-800 bg-slate-900/90 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className={`p-2.5 rounded-xl border ${getVerdictStyle(result.verdict).bg}`}>
                {getVerdictStyle(result.verdict).icon}
              </div>
              <div>
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Fact Verification Verdict</span>
                <h3 className="text-2xl font-bold text-white flex items-center gap-3">
                  {result.verdict}
                  <span className={`text-xs px-2.5 py-0.5 rounded-full font-semibold ${getVerdictStyle(result.verdict).badge}`}>
                    {result.confidence}% Confidence
                  </span>
                </h3>
              </div>
            </div>
          </div>

          <div className="p-6 space-y-6">
            {/* Objective Breakdown */}
            <div className="bg-slate-950/70 border border-slate-800/80 p-5 rounded-xl">
              <h4 className="font-semibold text-white text-sm mb-2 flex items-center gap-2">
                <BookOpen className="w-4 h-4 text-blue-400" />
                Factual Investigation Summary
              </h4>
              <p className="text-slate-300 text-sm leading-relaxed">{result.summary}</p>
            </div>

            {/* Recommendation */}
            {result.recommendation && (
              <div className="bg-blue-500/10 border border-blue-500/20 p-4 rounded-xl">
                <h4 className="font-semibold text-blue-300 text-sm mb-1">Consumer Guidance & Verification Advice:</h4>
                <p className="text-slate-300 text-sm">{result.recommendation}</p>
              </div>
            )}

            {/* Cited Sources */}
            {result.sources && result.sources.length > 0 && (
              <div>
                <h4 className="font-semibold text-white text-sm mb-3">Independent Fact-Checking References & Citations</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {result.sources.map((src, i) => (
                    <div
                      key={i}
                      className="bg-slate-950/70 border border-slate-800/80 p-4 rounded-xl flex flex-col justify-between space-y-3"
                    >
                      <div>
                        <div className="flex items-center justify-between gap-2 mb-1.5">
                          <span className="text-xs font-bold text-blue-400">{src.source_name}</span>
                          <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full uppercase ${
                            src.stance === 'REFUTES' ? 'bg-red-500/20 text-red-300' :
                            src.stance === 'SUPPORTS' ? 'bg-emerald-500/20 text-emerald-300' :
                            'bg-slate-800 text-slate-300'
                          }`}>
                            {src.stance}
                          </span>
                        </div>
                        <h5 className="text-sm font-semibold text-white line-clamp-1">{src.title}</h5>
                        <p className="text-xs text-slate-400 mt-2 line-clamp-2">{src.snippet}</p>
                      </div>

                      {src.url && (
                        <a
                          href={src.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1 text-xs text-blue-400 hover:text-blue-300 hover:underline pt-1"
                        >
                          <span>Visit reference portal</span>
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
