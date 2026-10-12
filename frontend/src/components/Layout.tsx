import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Navbar from './Navbar';

export default function Layout({ userName, onLogout }: { userName: string; onLogout?: () => void }) {
  return (
    <div className="flex min-h-screen bg-slate-950 font-sans text-slate-100 antialiased">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <Navbar userName={userName} onLogout={onLogout} />
        <main className="flex-1 p-6 md:p-8 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
