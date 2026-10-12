import { useState, useRef } from 'react';
import { 
  Image as ImageIcon, UploadCloud, CheckCircle2, 
  AlertTriangle, ShieldAlert, Cpu, Sparkles, RefreshCw, X
} from 'lucide-react';
import { api, type AnalysisResult } from '../api/client';

export default function AnalyzeImage() {
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (selectedFile: File) => {
    if (!selectedFile.type.startsWith('image/')) {
      setError("Please select a valid image file (.png, .jpg, .jpeg, .webp)");
      return;
    }
    setFile(selectedFile);
    setPreviewUrl(URL.createObjectURL(selectedFile));
    setError(null);
    setResult(null);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleAnalyze = async () => {
    if (!file) return;
    setIsAnalyzing(true);
    setError(null);
    setResult(null);

    try {
      const data = await api.analyzeImage(file);
      setResult(data);
    } catch (err: any) {
      console.error(err);
      setError(err?.response?.data?.detail || "Failed to analyze image file. Please check backend status.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setPreviewUrl(null);
    setResult(null);
    setError(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const getRiskBadge = (risk: string) => {
    switch (risk?.toLowerCase()) {
      case 'high':
        return {
          bg: 'bg-red-500/10 text-red-400 border border-red-500/30',
          badge: 'bg-red-600 text-white',
          icon: <ShieldAlert className="w-5 h-5 text-red-400" />
        };
      case 'medium':
        return {
          bg: 'bg-amber-500/10 text-amber-400 border border-amber-500/30',
          badge: 'bg-amber-600 text-white',
          icon: <AlertTriangle className="w-5 h-5 text-amber-400" />
        };
      default:
        return {
          bg: 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30',
          badge: 'bg-emerald-600 text-white',
          icon: <CheckCircle2 className="w-5 h-5 text-emerald-400" />
        };
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8 pb-12">
      <div>
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold uppercase tracking-wider mb-2">
          <Sparkles className="w-3.5 h-3.5" /> Computer Vision & ELA Forensics
        </div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight">Image Deepfake & Tampering Detector</h1>
        <p className="text-slate-400 mt-1">
          Perform Error Level Analysis (ELA), camera sensor noise variance inspection, and generative diffusion metadata checks.
        </p>
      </div>

      {/* Upload Box */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-xl overflow-hidden p-6">
        <input
          type="file"
          ref={fileInputRef}
          onChange={(e) => e.target.files?.[0] && handleFileSelect(e.target.files[0])}
          accept="image/png, image/jpeg, image/jpg, image/webp"
          className="hidden"
        />

        {!previewUrl ? (
          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className="border-2 border-dashed border-slate-700 hover:border-blue-500 rounded-xl p-12 text-center cursor-pointer transition-colors bg-slate-950/40 hover:bg-slate-950/70"
          >
            <div className="mx-auto w-14 h-14 bg-blue-500/10 rounded-2xl flex items-center justify-center text-blue-400 mb-4 border border-blue-500/20">
              <UploadCloud className="w-8 h-8" />
            </div>
            <h3 className="text-lg font-bold text-white">Drag and drop your image here</h3>
            <p className="text-sm text-slate-400 mt-1">or click to browse files (PNG, JPG, WebP up to 25MB)</p>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="relative bg-slate-950 rounded-xl border border-slate-800 p-4 flex flex-col md:flex-row items-center gap-6">
              <img
                src={previewUrl}
                alt="Selected preview"
                className="max-h-64 max-w-xs object-contain rounded-lg border border-slate-800"
              />
              <div className="flex-1 space-y-2 text-left">
                <h4 className="text-white font-semibold text-base">{file?.name}</h4>
                <p className="text-slate-400 text-xs">
                  File Size: {file ? (file.size / (1024 * 1024)).toFixed(2) : 0} MB
                </p>
                <p className="text-slate-400 text-xs">Type: {file?.type}</p>
                <div className="pt-2">
                  <button
                    onClick={handleReset}
                    className="flex items-center gap-1.5 text-xs text-red-400 hover:text-red-300 bg-red-500/10 hover:bg-red-500/20 px-3 py-1.5 rounded-lg border border-red-500/30 transition-colors cursor-pointer"
                  >
                    <X className="w-3.5 h-3.5" /> Remove Image
                  </button>
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-2">
              <button
                onClick={handleAnalyze}
                disabled={isAnalyzing}
                className={`flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl font-medium text-white transition-all shadow-lg ${
                  isAnalyzing
                    ? 'bg-blue-600/50 cursor-not-allowed'
                    : 'bg-blue-600 hover:bg-blue-500 shadow-blue-600/20 hover:shadow-blue-600/40 cursor-pointer'
                }`}
              >
                {isAnalyzing ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>Analyzing Image Forensics...</span>
                  </>
                ) : (
                  <>
                    <ImageIcon className="w-4 h-4" />
                    <span>Analyze Image Forensics</span>
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        {error && (
          <div className="mt-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
            {error}
          </div>
        )}
      </div>

      {/* Results Card */}
      {result && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-300">
          <div className="p-6 border-b border-slate-800 bg-slate-900/90 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className={`p-2.5 rounded-xl ${getRiskBadge(result.risk_level).bg}`}>
                {getRiskBadge(result.risk_level).icon}
              </div>
              <div>
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Vision Forensic Classification</span>
                <h3 className="text-2xl font-bold text-white flex items-center gap-3">
                  {result.prediction}
                  <span className={`text-xs px-2.5 py-0.5 rounded-full font-semibold ${getRiskBadge(result.risk_level).badge}`}>
                    {result.risk_level} Risk
                  </span>
                </h3>
              </div>
            </div>
          </div>

          <div className="p-6 space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-slate-950/70 border border-slate-800/80 p-4 rounded-xl">
                <p className="text-xs text-slate-400 font-medium">Confidence Level</p>
                <span className="text-3xl font-extrabold text-white mt-1 block">{result.confidence}%</span>
                <div className="w-full bg-slate-800 h-2 rounded-full mt-3 overflow-hidden">
                  <div
                    className={`h-full rounded-full ${
                      result.risk_level === 'High' ? 'bg-red-500' : result.risk_level === 'Medium' ? 'bg-amber-500' : 'bg-emerald-500'
                    }`}
                    style={{ width: `${result.confidence}%` }}
                  ></div>
                </div>
              </div>

              <div className="bg-slate-950/70 border border-slate-800/80 p-4 rounded-xl">
                <p className="text-xs text-slate-400 font-medium">Error Level Analysis (ELA)</p>
                <span className="text-2xl font-bold text-slate-200 mt-1 block">
                  Score: {result.metadata?.ela_score ?? 'N/A'}
                </span>
                <p className="text-xs text-slate-400 mt-2">
                  Measures localized compression discrepancies in high-frequency regions
                </p>
              </div>

              <div className="bg-slate-950/70 border border-slate-800/80 p-4 rounded-xl">
                <p className="text-xs text-slate-400 font-medium">Model Pipeline</p>
                <div className="mt-1 flex items-center gap-2 text-blue-400 font-semibold text-sm">
                  <Cpu className="w-4 h-4" />
                  <span>{result.model_name}</span>
                </div>
                <p className="text-xs text-slate-400 mt-2">
                  Dimensions: {result.metadata?.dimensions || 'Checked'}
                </p>
              </div>
            </div>

            <div className="bg-slate-950/70 border border-slate-800/80 p-5 rounded-xl">
              <h4 className="font-semibold text-white text-sm mb-2 flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-blue-400" />
                Forensic Analysis Explanation
              </h4>
              <p className="text-slate-300 text-sm leading-relaxed">{result.explanation}</p>
            </div>

            {result.key_factors && result.key_factors.length > 0 && (
              <div>
                <h4 className="font-semibold text-white text-sm mb-3">Forensic Detection Indicators</h4>
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
