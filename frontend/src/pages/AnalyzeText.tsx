import { useState } from 'react';
import { FileText, Send, AlertCircle } from 'lucide-react';
import axios from 'axios';

export default function AnalyzeText() {
  const [text, setText] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleAnalyze = async () => {
    if (!text.trim()) return;
    
    setIsAnalyzing(true);
    // Simulate API call for MVP
    setTimeout(() => {
      setIsAnalyzing(false);
      alert('Analysis feature will connect to FastAPI text endpoints in Phase 4.');
    }, 1500);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Analyze Text</h1>
        <p className="text-gray-500 mt-1">Detect fake news, misleading claims, and AI-generated text.</p>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        <div className="p-6 border-b border-gray-100 bg-gray-50 flex items-center gap-2">
          <FileText className="text-blue-600 w-5 h-5" />
          <h2 className="font-semibold text-gray-800">Submit Article or Claim</h2>
        </div>
        
        <div className="p-6">
          <textarea
            className="w-full h-64 p-4 text-gray-700 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none outline-none transition-shadow"
            placeholder="Paste news article content, headline, or a social media claim here to analyze..."
            value={text}
            onChange={(e) => setText(e.target.value)}
          ></textarea>
          
          <div className="mt-4 flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <AlertCircle className="w-4 h-4" />
              <span>Minimum 10 words recommended for accurate analysis.</span>
            </div>
            <button
              onClick={handleAnalyze}
              disabled={isAnalyzing || !text.trim()}
              className={`flex items-center gap-2 px-6 py-2.5 rounded-lg font-medium text-white transition-all ${
                isAnalyzing || !text.trim()
                  ? 'bg-blue-400 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700 hover:shadow-md'
              }`}
            >
              {isAnalyzing ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  Analyzing...
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  Analyze Content
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
