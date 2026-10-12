import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, FileText, Image, Video, Mic, CheckCircle, Clock } from 'lucide-react';

export default function Sidebar() {
  const location = useLocation();
  
  const navItems = [
    { name: 'Dashboard', path: '/', icon: <LayoutDashboard size={20} /> },
    { name: 'Analyze Text', path: '/analyze/text', icon: <FileText size={20} /> },
    { name: 'Analyze Image', path: '/analyze/image', icon: <Image size={20} /> },
    { name: 'Analyze Video', path: '/analyze/video', icon: <Video size={20} /> },
    { name: 'Analyze Audio', path: '/analyze/audio', icon: <Mic size={20} /> },
    { name: 'Fact-Check', path: '/fact-check', icon: <CheckCircle size={20} /> },
    { name: 'History', path: '/history', icon: <Clock size={20} /> },
  ];

  return (
    <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col h-screen sticky top-0">
      <div className="p-6 border-b border-slate-800">
        <h1 className="text-xl font-bold text-white flex items-center gap-2">
          <span className="bg-blue-600 p-1.5 rounded-lg">🛡️</span>
          TruthGuard Hub
        </h1>
      </div>
      
      <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
        <p className="px-4 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Analysis Menu</p>
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                isActive 
                  ? 'bg-blue-600 text-white shadow-md' 
                  : 'hover:bg-slate-800 hover:text-white'
              }`}
            >
              {item.icon}
              <span className="font-medium">{item.name}</span>
            </Link>
          );
        })}
      </nav>
      
      <div className="p-4 border-t border-slate-800">
        <div className="bg-slate-800 rounded-lg p-4 text-sm">
          <p className="text-slate-400 mb-2">System Status</p>
          <div className="flex items-center gap-2 text-green-400">
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
            </span>
            All systems operational
          </div>
        </div>
      </div>
    </aside>
  );
}
