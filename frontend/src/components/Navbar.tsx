import { useState } from 'react';
import { Bell, Search, LogOut } from 'lucide-react';

export default function Navbar({ userName, onLogout }: { userName: string; onLogout?: () => void }) {
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const handleLogout = () => {
    if (onLogout) {
      onLogout();
    } else {
      window.location.href = "/login";
    }
  };

  return (
    <header className="bg-slate-900 border-b border-slate-800 h-16 flex items-center justify-between px-6 sticky top-0 z-20">
      <div className="flex items-center bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 w-72 md:w-96">
        <Search className="text-slate-500 w-4 h-4 mr-2" />
        <input 
          type="text" 
          placeholder="Search detection models, reports, claims..." 
          className="bg-transparent border-none outline-none text-xs text-slate-200 placeholder-slate-500 w-full"
        />
      </div>
      
      <div className="flex items-center gap-3">
        <div className="hidden sm:flex items-center gap-1.5 px-3 py-1 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-full text-xs font-medium">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>Groq Neural Active</span>
        </div>

        <button className="relative p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-xl transition-colors cursor-pointer">
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-blue-500 rounded-full"></span>
        </button>

        <div className="h-6 w-px bg-slate-800 mx-1"></div>
        
        <div className="relative">
          <button 
            onClick={() => setDropdownOpen(!dropdownOpen)}
            className="flex items-center gap-2 cursor-pointer hover:bg-slate-800 p-1.5 rounded-xl transition-colors"
          >
            <div className="w-8 h-8 bg-blue-600 text-white rounded-lg flex items-center justify-center font-bold text-xs shadow-sm uppercase">
              {userName ? userName.charAt(0) : 'A'}
            </div>
            <div className="text-left hidden md:block">
              <span className="text-xs font-semibold text-slate-200 block">{userName || 'Admin'}</span>
              <span className="text-[10px] text-slate-400 block">Investigator</span>
            </div>
          </button>
          
          {dropdownOpen && (
            <div className="absolute top-full mt-2 right-0 bg-slate-900 border border-slate-800 shadow-2xl rounded-xl py-1.5 w-48 z-50 animate-in fade-in zoom-in-95 duration-150">
              <div className="px-4 py-2 border-b border-slate-800">
                <p className="text-xs font-semibold text-white">{userName}</p>
                <p className="text-[10px] text-slate-400">TruthGuard Verified</p>
              </div>

              <button 
                onClick={handleLogout}
                className="flex items-center gap-2 text-xs text-red-400 hover:bg-slate-800 px-4 py-2 w-full text-left transition-colors cursor-pointer mt-1"
              >
                <LogOut className="w-3.5 h-3.5" />
                Sign out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
