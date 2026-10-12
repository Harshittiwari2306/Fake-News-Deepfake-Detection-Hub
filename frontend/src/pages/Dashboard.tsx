import { Activity, AlertTriangle, CheckCircle, ShieldAlert } from 'lucide-react';

export default function Dashboard() {
  const stats = [
    { title: 'Total Analyses', value: '1,284', icon: <Activity className="w-6 h-6 text-blue-500" />, trend: '+12% from last week' },
    { title: 'Fake News Detected', value: '342', icon: <AlertTriangle className="w-6 h-6 text-amber-500" />, trend: '+5% from last week' },
    { title: 'Deepfakes Identified', value: '89', icon: <ShieldAlert className="w-6 h-6 text-red-500" />, trend: '-2% from last week' },
    { title: 'Verified Authentic', value: '853', icon: <CheckCircle className="w-6 h-6 text-green-500" />, trend: '+18% from last week' },
  ];

  const recentAnalyses = [
    { id: 'AN-1029', type: 'Text', status: 'Potentially Misleading', confidence: '87%', date: '2 mins ago', color: 'text-amber-600 bg-amber-50' },
    { id: 'AN-1028', type: 'Image', status: 'Likely Manipulated', confidence: '94%', date: '15 mins ago', color: 'text-red-600 bg-red-50' },
    { id: 'AN-1027', type: 'Video', status: 'Authentic', confidence: '98%', date: '1 hour ago', color: 'text-green-600 bg-green-50' },
    { id: 'AN-1026', type: 'Text', status: 'Authentic', confidence: '91%', date: '3 hours ago', color: 'text-green-600 bg-green-50' },
  ];

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard Overview</h1>
          <p className="text-gray-500 mt-1">Platform analytics and recent detection activities.</p>
        </div>
        <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors shadow-sm">
          Generate Report
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, i) => (
          <div key={i} className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-sm font-medium text-gray-500 mb-1">{stat.title}</p>
                <h3 className="text-3xl font-bold text-gray-900">{stat.value}</h3>
              </div>
              <div className="p-2 bg-gray-50 rounded-lg">
                {stat.icon}
              </div>
            </div>
            <p className="text-xs text-gray-500 mt-4">{stat.trend}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white rounded-xl border border-gray-200 shadow-sm p-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4">Detection Trends</h2>
          <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg border border-dashed border-gray-300">
            <p className="text-gray-500 flex items-center gap-2">
              <Activity className="w-5 h-5" />
              Chart visualization placeholder (Recharts will be added here)
            </p>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-bold text-gray-900">Recent Analyses</h2>
            <button className="text-sm text-blue-600 hover:underline">View all</button>
          </div>
          <div className="space-y-4">
            {recentAnalyses.map((item, i) => (
              <div key={i} className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg transition-colors border border-transparent hover:border-gray-100">
                <div>
                  <p className="text-sm font-semibold text-gray-900">{item.id} <span className="text-gray-500 font-normal ml-1">({item.type})</span></p>
                  <p className="text-xs text-gray-500">{item.date}</p>
                </div>
                <div className="text-right">
                  <span className={`inline-block px-2.5 py-1 text-xs font-medium rounded-full ${item.color}`}>
                    {item.status} ({item.confidence})
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
