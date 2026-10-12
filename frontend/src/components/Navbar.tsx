import { useState } from 'react';
import { Bell, Search, LogOut, Settings } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Navbar({ userName }: { userName: string }) {
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const handleLogout = () => {
    // In a real app we'd clear context/token
    window.location.href = "/login";
  };

  return (
    <header className="bg-white border-b border-gray-200 h-16 flex items-center justify-between px-6 sticky top-0 z-10">
      <div className="flex items-center bg-gray-100 rounded-lg px-3 py-2 w-96">
        <Search className="text-gray-400 w-5 h-5 mr-2" />
        <input 
          type="text" 
          placeholder="Search analyses, reports..." 
          className="bg-transparent border-none outline-none text-sm w-full"
        />
      </div>
      
      <div className="flex items-center gap-4">
        <button className="relative p-2 text-gray-500 hover:bg-gray-100 rounded-full transition-colors">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full"></span>
        </button>
        <div className="h-8 w-px bg-gray-200 mx-2"></div>
        
        <div className="relative">
          <button 
            onClick={() => setDropdownOpen(!dropdownOpen)}
            className="flex items-center gap-2 cursor-pointer hover:bg-gray-50 p-1.5 rounded-lg transition-colors"
          >
            <div className="w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-bold uppercase">
              {userName ? userName.charAt(0) : 'U'}
            </div>
            <span className="text-sm font-medium text-gray-700">{userName || 'User'}</span>
          </button>
          
          {dropdownOpen && (
            <div className="absolute top-full mt-2 right-0 bg-white border border-gray-200 shadow-lg rounded-lg py-2 w-48 z-50">
              <Link 
                to="/settings"
                onClick={() => setDropdownOpen(false)}
                className="flex items-center gap-2 text-sm text-gray-700 hover:bg-gray-50 px-4 py-2 w-full text-left transition-colors"
              >
                <Settings className="w-4 h-4" />
                Settings
              </Link>
              <button 
                onClick={handleLogout}
                className="flex items-center gap-2 text-sm text-red-600 hover:bg-red-50 px-4 py-2 w-full text-left transition-colors"
              >
                <LogOut className="w-4 h-4" />
                Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
