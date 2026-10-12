import { useState } from 'react';
import { 
  FileText, Send, AlertCircle, CheckCircle2, AlertTriangle, 
  ShieldAlert, Sparkles, Cpu, Clock, RefreshCw, Copy, Check 
} from 'lucide-react';
import { api, type AnalysisResult } from '../api/client';

export default function AnalyzeText() {
  const [text, setText] = useState('');
  const [headline, setHeadline] = useState('');
  const [sourceUrl, setSourceUrl] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const sampleClaims = [
    {
      title: "Extraterrestrial Antarctic Discovery",
      text: "BREAKING: NASA whistleblowers confirm that a massive pyramid and alien city were uncovered 2 miles beneath Antarctica's melting ice sheets. Government officials have ordered an immediate media blackout.",
      headline: "Alien City Uncovered in Antarctica",
    },
    {
      title: "Scientific Fusion Breakthrough",
      text: "Researchers at the National Ignition Facility have achieved net energy gain in a controlled nuclear fusion reaction, verifying results through repeated peer-reviewed trials published in Nature.",
      headline: "Fusion Energy Milestone Verified by Physicists",
    },
    {
      title: "Secret Water Fluoride Chip",
      text: "URGENT WARNING: Declassified documents prove tap water contains microscopic nanotechnology chips designed to monitor citizen biometrics. Throw away your tap water immediately!",
      headline: "Secret Nanotech Discovered in Drinking Water",
    }
  ];

  const handleAnalyze = async () => {
    if (!text.trim()) return;
    
    setIsAnalyzing(true);
    setError(null);
    setResult(null);

    try {
      const data = await api.analyzeText({
        text,
        headline: headline.trim() || undefined,
        source_url: sourceUrl.trim() || undefined,
      });
      setResult(data);
    } catch (err: any) {
      console.error(err);
      setError(err?.response?.data?.detail || "Failed to analyze text. Please verify backend connection.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleCopyReport = () => {
    if (!result) return;
    const report = `TruthGuard Misinformation Report
Prediction: ${result.prediction}
Confidence: ${result.confidence}%
Risk Level: ${result.risk_level}
Model: ${result.model_name}
Reasoning: ${result.explanation}
Key Factors: ${(result.key_factors || []).join(', ')}`;
    navigator.clipboard.writeText(report);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getRiskColor = (risk: string) => {
    switch (risk?.toLowerCase()) {
      case 'high':
        return {
          bg: 'bg-red-500/10 border-red-500/30 text-red-400',
          badge: 'bg-red-600 text-white',
          border: 'border-red-500',
          icon: <ShieldAlert className="w-5 h-5 text-red-400" />
        };
      case 'medium':
        return {
          bg: 'bg-amber-500/10 border-amber-500/30 text-amber-400',
          badge: 'bg-amber-600 text-white',
          border: 'border-amber-500',
          icon: <AlertTriangle className="w-5 h-5 text-amber-400" />
        };
      default:
        return {
          bg: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400',
          badge: 'bg-emerald-600 text-white',
          border: 'border-emerald-500',
          icon: <CheckCircle2 className="w-5 h-5 text-emerald-400" />
        };
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8 pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold uppercase tracking-wider mb-2">
            <Sparkles className="w-3.5 h-3.5" /> Groq AI Misinformation Detection
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">Analyze Text & News Claims</h1>
          <p className="text-slate-400 mt-1">
            Detect fabricated stories, hyper-partisan manipulation, and synthetic AI-generated text using real-time Groq neural inference.
          </p>
        </div>
      </div>

      {/* Quick Test Samples */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4">
        <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
          ⚡ Quick Demo Samples (Click to load):
        </p>
        <div className="flex flex-wrap gap-2">
          {sampleClaims.map((sample, idx) => (
            <button
              key={idx}
              onClick={() => {
                setText(sample.text);
                setHeadline(sample.headline);
              }}
              className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white px-3 py-1.5 rounded-lg border border-slate-700/60 transition-all flex items-center gap-1.5 cursor-pointer"
            >
              <span>{sample.title}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Input Box Card */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-xl overflow-hidden">
        <div className="p-5 border-b border-slate-800 bg-slate-900/80 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FileText className="text-blue-400 w-5 h-5" />
            <h2 className="font-semibold text-white">Input News Article or Social Post</h2>
          </div>
          <span className="text-xs text-slate-400">{text.length} characters</span>
        </div>

        <div className="p-6 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Headline (Optional)</label>
              <input
                type="text"
                placeholder="e.g. Breaking: Major Announcement..."
                value={headline}
                onChange={(e) => setHeadline(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3.5 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Source URL (Optional)</label>
              <input
                type="url"
                placeholder="https://example.com/article"
                value={sourceUrl}
                onChange={(e) => setSourceUrl(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3.5 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Full Article / Claim Text *</label>
            <textarea
              className="w-full h-48 bg-slate-950 border border-slate-800 rounded-xl p-4 text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all resize-none text-sm leading-relaxed"
              placeholder="Paste article body, tweet, WhatsApp message, or news claim here to analyze for misinformation..."
              value={text}
              onChange={(e) => setText(e.target.value)}
            ></textarea>
          </div>

          {error && (
            <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg flex items-center gap-2 text-red-400 text-sm">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2">
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <AlertCircle className="w-4 h-4 text-blue-400" />
              <span>Full neural analysis processes claims against linguistic and factual indicators.</span>
            </div>
            
            <button
              onClick={handleAnalyze}
              disabled={isAnalyzing || !text.trim()}
              className={`w-full sm:w-auto flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl font-medium text-white transition-all shadow-lg ${
                isAnalyzing || !text.trim()
                  ? 'bg-blue-600/50 cursor-not-allowed text-slate-300'
                  : 'bg-blue-600 hover:bg-blue-500 shadow-blue-600/20 hover:shadow-blue-600/40 cursor-pointer active:scale-95'
              }`}
            >
              {isAnalyzing ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Processing with Groq AI...</span>
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  <span>Analyze with Groq AI</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Analysis Results Display */}
      {result && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-300">
          {/* Result Banner */}
          <div className="p-6 border-b border-slate-800 bg-slate-900/90 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className={`p-2.5 rounded-xl border ${getRiskColor(result.risk_level).bg}`}>
                {getRiskColor(result.risk_level).icon}
              </div>
              <div>
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">AI Classification Verdict</span>
                <h3 className="text-2xl font-bold text-white flex items-center gap-3">
                  {result.prediction}
                  <span className={`text-xs px-2.5 py-0.5 rounded-full font-semibold ${getRiskColor(result.risk_level).badge}`}>
                    {result.risk_level} Risk
                  </span>
                </h3>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={handleCopyReport}
                className="flex items-center gap-1.5 text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3.5 py-2 rounded-lg border border-slate-700 transition-colors cursor-pointer"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-green-400" /> : <Copy className="w-3.5 h-3.5" />}
                {copied ? 'Copied' : 'Copy Report'}
              </button>
            </div>
          </div>

          <div className="p-6 space-y-6">
            {/* Key Metrics Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-slate-950/70 border border-slate-800/80 p-4 rounded-xl">
                <p className="text-xs text-slate-400 font-medium">Confidence Score</p>
                <div className="mt-2 flex items-baseline gap-2">
                  <span className="text-3xl font-extrabold text-white">{result.confidence}%</span>
                </div>
                <div className="w-full bg-slate-800 h-2 rounded-full mt-3 overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      result.risk_level === 'High' ? 'bg-red-500' : result.risk_level === 'Medium' ? 'bg-amber-500' : 'bg-emerald-500'
                    }`}
                    style={{ width: `${result.confidence}%` }}
                  ></div>
                </div>
              </div>

              <div className="bg-slate-950/70 border border-slate-800/80 p-4 rounded-xl">
                <p className="text-xs text-slate-400 font-medium">Sentiment / Tone Profile</p>
                <div className="mt-2">
                  <span className="text-xl font-bold text-slate-200">
                    {result.metadata?.sentiment || 'Sensationalist'}
                  </span>
                  <p className="text-xs text-slate-400 mt-2">
                    Linguistic sentiment indicators detected in claim tokens
                  </p>
                </div>
              </div>

              <div className="bg-slate-950/70 border border-slate-800/80 p-4 rounded-xl">
                <p className="text-xs text-slate-400 font-medium">Model Provenance</p>
                <div className="mt-2 flex items-center gap-2 text-blue-400 font-semibold text-sm">
                  <Cpu className="w-4 h-4" />
                  <span>{result.model_name}</span>
                </div>
                <div className="flex items-center gap-1.5 text-xs text-slate-400 mt-3">
                  <Clock className="w-3.5 h-3.5" />
                  <span>Verified at {new Date(result.created_at || Date.now()).toLocaleTimeString()}</span>
                </div>
              </div>
            </div>

            {/* Explainable AI Reasoning */}
            <div className="bg-slate-950/70 border border-slate-800/80 p-5 rounded-xl">
              <div className="flex items-center gap-2 mb-2">
                <Sparkles className="w-4 h-4 text-blue-400" />
                <h4 className="font-semibold text-white text-sm">Explainable AI Analysis & Reasoning</h4>
              </div>
              <p className="text-slate-300 text-sm leading-relaxed">
                {result.explanation}
              </p>
            </div>

            {/* Key Risk Factors */}
            {result.key_factors && result.key_factors.length > 0 && (
              <div>
                <h4 className="font-semibold text-white text-sm mb-3">Key Risk Factors & Detection Indicators</h4>
                <div className="space-y-2">
                  {result.key_factors.map((factor, i) => (
                    <div
                      key={i}
                      className="flex items-start gap-3 p-3 bg-slate-950/40 border border-slate-800/80 rounded-lg text-sm text-slate-300"
                    >
                      <span className="w-1.5 h-1.5 rounded-full bg-blue-400 mt-2 shrink-0"></span>
                      <span>{factor}</span>
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
